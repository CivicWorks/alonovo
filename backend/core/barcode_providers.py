"""Barcode lookup provider chain.

Tries multiple product databases in order until one returns a result.
Caches results in BarcodeCache to avoid repeated external API calls.

To add a new provider:
    1. Subclass BarcodeProvider
    2. Implement lookup() and name property
    3. Append instance to PROVIDER_CHAIN
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List

import requests

from .models import BarcodeCache


USER_AGENT = "Alonovo/1.0 (contact@cooperation.org)"
REQUEST_TIMEOUT = 10


@dataclass
class ProductInfo:
    barcode: str
    product_name: str
    brands: str           # comma-separated
    owner: str            # manufacturer/owner field
    categories: str
    image_url: str
    ecoscore_grade: str
    provider: str
    raw_response: dict


class BarcodeProvider(ABC):
    """Base class for barcode lookup providers."""

    @abstractmethod
    def lookup(self, barcode: str) -> Optional[ProductInfo]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class OpenProductOpenerProvider(BarcodeProvider):
    """Provider for any Open *  Facts API (all use the same Product Opener system)."""

    def __init__(self, base_url: str, provider_name: str):
        self._base_url = base_url.rstrip('/')
        self._name = provider_name

    @property
    def name(self) -> str:
        return self._name

    def lookup(self, barcode: str) -> Optional[ProductInfo]:
        url = f"{self._base_url}/api/v2/product/{barcode}"
        params = {
            "fields": "product_name,brands,owner,categories,image_url,ecoscore_grade"
        }
        resp = requests.get(
            url,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        if data.get("status") != 1:
            return None

        product = data.get("product", {})
        product_name = product.get("product_name", "").strip()
        if not product_name:
            return None

        return ProductInfo(
            barcode=barcode,
            product_name=product_name,
            brands=product.get("brands", ""),
            owner=product.get("owner", ""),
            categories=product.get("categories", ""),
            image_url=product.get("image_url", ""),
            ecoscore_grade=product.get("ecoscore_grade", ""),
            provider=self.name,
            raw_response=data,
        )


# Provider chain — tried in order, first hit wins
PROVIDER_CHAIN: List[BarcodeProvider] = [
    OpenProductOpenerProvider("https://world.openfoodfacts.net", "open_food_facts"),
    OpenProductOpenerProvider("https://world.openbeautyfacts.org", "open_beauty_facts"),
    OpenProductOpenerProvider("https://world.openproductsfacts.org", "open_products_facts"),
    OpenProductOpenerProvider("https://world.openpetfoodfacts.org", "open_pet_food_facts"),
]


def lookup_barcode(barcode: str) -> Optional[ProductInfo]:
    """Look up a barcode, checking cache first, then trying each provider.

    Returns ProductInfo or None if no provider has the product.
    Caches successful lookups in BarcodeCache.
    """
    # Check cache first
    cached = BarcodeCache.objects.filter(barcode=barcode).first()
    if cached:
        return ProductInfo(
            barcode=cached.barcode,
            product_name=cached.product_name,
            brands=cached.brands,
            owner=cached.owner,
            categories=cached.categories,
            image_url=cached.image_url,
            ecoscore_grade=cached.raw_response.get("product", {}).get("ecoscore_grade", ""),
            provider=cached.provider,
            raw_response=cached.raw_response,
        )

    # Try each provider in order
    for provider in PROVIDER_CHAIN:
        try:
            result = provider.lookup(barcode)
            if result:
                # Cache the result
                BarcodeCache.objects.create(
                    barcode=barcode,
                    product_name=result.product_name,
                    brands=result.brands,
                    owner=result.owner,
                    categories=result.categories,
                    image_url=result.image_url,
                    provider=result.provider,
                    raw_response=result.raw_response,
                )
                return result
        except requests.RequestException:
            continue

    return None
