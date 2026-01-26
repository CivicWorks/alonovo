from rest_framework import serializers
from .models import Company, CompanyScore


class CompanyScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyScore
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    scores = CompanyScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = '__all__'
