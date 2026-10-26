"""Read-only browser for the data, open to anyone without signing in.

A second Django admin site mounted at /admin/browse/. Anyone can list, search, filter and open
records; nobody can add, change or delete through it. Only the models below are on it.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import BrandMapping, Company, Deal, Product


class BrowseSite(admin.AdminSite):
    site_header = 'Alonovo data'
    site_title = 'Alonovo data'
    index_title = 'Products, companies and brands'
    site_url = None
    enable_nav_sidebar = False
    index_template = 'admin/browse_index.html'

    def has_permission(self, request):
        return request.method in ('GET', 'HEAD')

    def each_context(self, request):
        context = super().each_context(request)
        # Hides the "Welcome / Log out" bar, which means nothing to someone not signed in
        context['has_permission'] = False
        return context


browse_site = BrowseSite(name='browse')


class ReadOnlyAdmin(admin.ModelAdmin):
    actions = None
    list_per_page = 50

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return True


def usda_record(product):
    return ((product.attributes or {}).get('usda_fdc') or {}).get('record') or {}


@admin.register(Product, site=browse_site)
class ProductBrowse(ReadOnlyAdmin):
    list_display = ['picture', 'name', 'brand_name', 'company', 'category', 'product_type', 'barcode']
    list_display_links = ['name']
    list_filter = ['category', 'source']
    search_fields = ['name', 'brand_name', 'barcode', 'category', 'product_type', 'company__name', 'company__ticker']
    list_select_related = ['company']
    fields = ['picture_large', 'name', 'brand_name', 'company', 'category', 'product_type', 'barcode',
              'typical_price', 'ingredients', 'nutrition', 'source', 'attributes', 'updated_at']

    @admin.display(description='')
    def picture(self, obj):
        return format_html('<img src="{}" style="height:40px">', obj.image_url) if obj.image_url else ''

    @admin.display(description='Picture')
    def picture_large(self, obj):
        return format_html('<img src="{}" style="max-height:160px">', obj.image_url) if obj.image_url else '-'

    @admin.display(description='Ingredients')
    def ingredients(self, obj):
        return usda_record(obj).get('ingredients') or '-'

    @admin.display(description='Nutrition per 100 g')
    def nutrition(self, obj):
        rows = [(n['nutrient']['name'], n.get('amount'), n['nutrient'].get('unitName', ''))
                for n in usda_record(obj).get('foodNutrients', []) if n.get('nutrient')]
        if not rows:
            return '-'
        return format_html('<table>{}</table>', format_html(''.join(
            format_html('<tr><td>{}</td><td>{} {}</td></tr>', name, amount, unit) for name, amount, unit in rows)))


@admin.register(Company, site=browse_site)
class CompanyBrowse(ReadOnlyAdmin):
    list_display = ['name', 'ticker', 'sector', 'website']
    list_filter = ['sector']
    search_fields = ['name', 'ticker']
    fields = ['name', 'ticker', 'sector', 'website', 'uri']


@admin.register(BrandMapping, site=browse_site)
class BrandMappingBrowse(ReadOnlyAdmin):
    list_display = ['brand_name', 'company', 'role', 'source']
    search_fields = ['brand_name', 'company__name']
    list_select_related = ['company']


@admin.register(Deal, site=browse_site)
class DealBrowse(ReadOnlyAdmin):
    list_display = ['title', 'brand_name', 'company', 'store_name', 'category', 'price', 'regular_price', 'source', 'last_seen_at']
    list_filter = ['category', 'source', 'store_name']
    search_fields = ['title', 'brand_name', 'company__name', 'store_name']
    list_select_related = ['company']
