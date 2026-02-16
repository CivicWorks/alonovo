"""Brand-to-company matching logic.

Given product info from a barcode scan, find the parent company
in the Alonovo database.
"""
from typing import Optional, Tuple

from .models import BrandMapping, Company
from .barcode_providers import ProductInfo


def match_brand_to_company(product_info: ProductInfo) -> Tuple[Optional[Company], float, str]:
    """Match a product's brand info to a company in the database.

    Returns (company, confidence, method) where method describes how the match was found.

    Matching order:
    1. Exact brand_name_normalized match in BrandMapping
    2. Owner field match in BrandMapping
    3. Fuzzy (icontains) brand match in BrandMapping
    4. Direct Company.name exact match
    5. Fuzzy Company.name match
    6. Owner as Company.name match
    """
    brand_names = [b.strip() for b in product_info.brands.split(",") if b.strip()]
    owner = product_info.owner.strip()

    # Also try cleaning common owner prefixes from Open Food Facts
    # e.g., "org-ferrero-france-commerciale" -> "ferrero"
    cleaned_owner = _clean_owner(owner)

    # Step 1: Exact match on brand_name_normalized
    for brand in brand_names:
        normalized = brand.lower().strip()
        mapping = BrandMapping.objects.filter(brand_name_normalized=normalized).first()
        if mapping:
            return (mapping.company, mapping.confidence, "brand_mapping_exact")

    # Step 2: Owner field match
    for owner_variant in [owner, cleaned_owner]:
        if owner_variant:
            normalized = owner_variant.lower().strip()
            mapping = BrandMapping.objects.filter(brand_name_normalized=normalized).first()
            if mapping:
                return (mapping.company, mapping.confidence * 0.9, "owner_mapping")

    # Step 3: Fuzzy brand match in BrandMapping
    for brand in brand_names:
        normalized = brand.lower().strip()
        if len(normalized) >= 3:
            mapping = BrandMapping.objects.filter(
                brand_name_normalized__icontains=normalized
            ).first()
            if mapping:
                return (mapping.company, mapping.confidence * 0.7, "brand_mapping_fuzzy")

    # Step 4: Direct Company.name exact match (brand IS the company)
    for brand in brand_names:
        company = Company.objects.filter(name__iexact=brand).first()
        if company:
            return (company, 0.8, "company_name_exact")

    # Step 5: Fuzzy Company.name match
    for brand in brand_names:
        if len(brand) >= 3:
            company = Company.objects.filter(name__icontains=brand).first()
            if company:
                return (company, 0.5, "company_name_fuzzy")

    # Step 6: Try owner as company name
    for owner_variant in [owner, cleaned_owner]:
        if owner_variant:
            company = Company.objects.filter(name__iexact=owner_variant).first()
            if company:
                return (company, 0.7, "owner_company_match")

    return (None, 0.0, "not_found")


def _clean_owner(owner: str) -> str:
    """Clean Open Food Facts owner field.

    Open Food Facts uses formats like "org-ferrero-france-commerciale".
    Extract the company name part.
    """
    if not owner:
        return ""
    # Remove common prefixes
    cleaned = owner
    for prefix in ["org-", "user-"]:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):]
    # Take first segment (before country/subsidiary qualifiers)
    parts = cleaned.split("-")
    if len(parts) > 1:
        # Try just the first word as the company name
        return parts[0].strip()
    return cleaned.strip()
