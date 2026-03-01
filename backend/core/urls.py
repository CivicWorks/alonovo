from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, ValueViewSet, current_user, user_weights, sectors_list, company_claims, products_list, product_categories
from .views_mobile import barcode_scan, alternatives_for_company, brand_mappings_list

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'values', ValueViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('me/', current_user, name='current-user'),
    path('me/weights/', user_weights, name='user-weights'),
    path('sectors/', sectors_list, name='sectors-list'),
    path('companies/<str:ticker>/claims/', company_claims, name='company-claims'),
    # Mobile app endpoints
    path('scan/', barcode_scan, name='barcode-scan'),
    path('alternatives/<str:ticker>/', alternatives_for_company, name='alternatives'),
    path('brands/', brand_mappings_list, name='brand-mappings'),
    # Product endpoints
    path('products/', products_list, name='products-list'),
    path('products/categories/', product_categories, name='product-categories'),
]
