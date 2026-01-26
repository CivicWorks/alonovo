from django.db import models


class Claim(models.Model):
    """LinkedClaim storage - real fields, not JSONB

    Spec: https://identity.foundation/labs-linkedclaims/
    """
    uri = models.CharField(max_length=500, unique=True)
    subject = models.CharField(max_length=500, db_index=True)
    object = models.CharField(max_length=500, blank=True)
    claim = models.CharField(max_length=100)
    statement = models.TextField(blank=True)
    effective_date = models.DateField(null=True, blank=True)
    source_uri = models.CharField(max_length=500, blank=True)
    how_known = models.CharField(max_length=50, blank=True)
    date_observed = models.DateField(null=True, blank=True)
    digest_multibase = models.CharField(max_length=200, blank=True)
    score = models.FloatField(null=True, blank=True)
    aspect = models.CharField(max_length=100, blank=True)
    amt = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=300, blank=True)
    curator = models.CharField(max_length=300, blank=True)
    issuer_id = models.CharField(max_length=300, blank=True)
    issuer_id_type = models.CharField(max_length=20, blank=True)
    proof = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.claim}: {self.subject}"


class Company(models.Model):
    uri = models.CharField(max_length=500, unique=True)
    ticker = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return f"{self.ticker} - {self.name}"


class CompanyScore(models.Model):
    """Simplified snapshot for Phase 1. Will become CompanyValueSnapshot later."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='scores')
    score = models.FloatField()
    grade = models.CharField(max_length=5)
    raw_value = models.FloatField()
    reason = models.TextField(blank=True)
    computed_at = models.DateTimeField(auto_now_add=True)
    source_claim_uris = models.JSONField(default=list)

    def __str__(self):
        return f"{self.company.ticker}: {self.grade}"
