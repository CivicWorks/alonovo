from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CompanyViewSet, ValueViewSet, current_user, user_weights,
                     sectors_list, company_claims, vote_for_company, vote_leaderboard)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'values', ValueViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('me/', current_user, name='current-user'),
    path('me/weights/', user_weights, name='user-weights'),
    path('sectors/', sectors_list, name='sectors-list'),
    path('companies/<str:ticker>/claims/', company_claims, name='company-claims'),
    path('companies/<str:ticker>/vote/', vote_for_company, name='company-vote'),
    path('votes/leaderboard/', vote_leaderboard, name='vote-leaderboard'),
]
