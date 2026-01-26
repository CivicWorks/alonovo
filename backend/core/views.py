from rest_framework import viewsets
from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.prefetch_related('scores')
    serializer_class = CompanySerializer
    lookup_field = 'ticker'
