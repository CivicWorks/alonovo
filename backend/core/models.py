from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Claim(models.Model):
    """LinkedClaim storage - immutable source facts with provenance

    Spec: https://identity.foundation/labs-linkedclaims/
    """
    uri = models.CharField(max_length=500, unique=True)
    subject = models.CharField(max_length=500, db_index=True)
    object = models.CharField(max_length=500, blank=True)
    claim_type = models.CharField(max_length=100, db_index=True)
    statement = models.TextField(blank=True)
    effective_date = models.DateField(null=True, blank=True)
    source_uri = models.CharField(max_length=500, blank=True)
    how_known = models.CharField(max_length=50, blank=True)
    date_observed = models.DateField(null=True, blank=True)
    digest_multibase = models.CharField(max_length=200, blank=True)
    amt = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    label = models.CharField(max_length=100, blank=True)
    author = models.CharField(max_length=300, blank=True)
    curator = models.CharField(max_length=300, blank=True)
    issuer_id = models.CharField(max_length=300, blank=True)
    issuer_id_type = models.CharField(max_length=20, blank=True)
    proof = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Immutable after creation
        if self.pk:
            raise ValidationError("Claims are immutable and cannot be updated")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.claim_type}: {self.subject}"


class Company(models.Model):
    uri = models.CharField(max_length=500, unique=True)
    ticker = models.CharField(max_length=10, db_index=True, null=True, blank=True)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "companies"
        ordering = ['name']

    def __str__(self):
        return f"{self.ticker} - {self.name}" if self.ticker else self.name


class Value(models.Model):
    """Admin-defined criterion for scoring companies.

    Three types:
    - metric: numeric data with thresholds (e.g., lobbying spend)
    - label: categorical certifications (e.g., cage-free, B Corp)
    - categorical_grade: labels that map to severity grades (e.g., ICE involvement)
    """
    VALUE_TYPES = [
        ('metric', 'Metric'),
        ('label', 'Label'),
        ('categorical_grade', 'Categorical Grade'),
    ]

    slug = models.SlugField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    value_type = models.CharField(max_length=20, choices=VALUE_TYPES)

    # Platform policy flags
    is_fixed = models.BooleanField(default=False, help_text="User cannot adjust weight to zero")
    is_disqualifying = models.BooleanField(default=False, help_text="F on this = F overall")
    min_weight = models.IntegerField(default=0, help_text="Floor that user cannot go below")

    # Display grouping (frontend collapses values with same display_group)
    display_group = models.CharField(max_length=100, blank=True, default='',
        help_text='Group name for frontend collapse. Empty = show individually.')
    display_group_order = models.IntegerField(default=0,
        help_text='Sort order for groups and ungrouped values in UI')

    # Card display
    card_display_template = models.CharField(max_length=200, blank=True,
        help_text='Template like "${amt}M ({year})" for card display')
    card_icon = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ScoringRule(models.Model):
    """How to grade a value. Versioned for historical tracking."""
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='scoring_rules')
    version = models.IntegerField(default=1)
    config = models.JSONField(default=dict, help_text="Thresholds for metrics, label→grade maps for categorical")
    effective_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['value', 'version']

    def __str__(self):
        return f"{self.value.name} v{self.version}"


class CompanyValueSnapshot(models.Model):
    """Pre-computed score per company per value.

    Points back to source claims via URIs.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='value_snapshots')
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='snapshots')

    score = models.FloatField()  # -1 to 1
    grade = models.CharField(max_length=5)
    claim_uris = models.JSONField(default=list, help_text="URIs of claims this score derived from")

    # Validation
    validation_count = models.IntegerField(default=0)
    dispute_count = models.IntegerField(default=0)

    # Card display
    highlight_on_card = models.BooleanField(default=False)
    highlight_priority = models.IntegerField(default=0, help_text="Higher = shown first")
    display_text = models.CharField(max_length=200, blank=True, help_text='Pre-rendered, e.g., "Lobbying: $11.1M (2024)"')
    display_icon = models.CharField(max_length=50, blank=True)

    # Provenance
    scoring_rule_version = models.IntegerField(default=1)
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['company', 'value']

    def __str__(self):
        return f"{self.company.ticker} - {self.value.name}: {self.grade}"


class UserValueWeight(models.Model):
    """User's personal weight multipliers for values."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='value_weights')
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='user_weights')
    weight = models.IntegerField(default=5)  # 0-10 scale

    class Meta:
        unique_together = ['user', 'value']

    def __str__(self):
        return f"{self.user.username} - {self.value.name}: {self.weight}"


class CompanyBadge(models.Model):
    """Badges displayed on company cards - positive, negative, or neutral indicators."""
    BADGE_TYPES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='badges')
    label = models.CharField(max_length=200)
    badge_type = models.CharField(max_length=10, choices=BADGE_TYPES)
    value = models.ForeignKey(Value, on_delete=models.SET_NULL, null=True, blank=True,
                              help_text="The value this badge was derived from")
    source_claim_uri = models.CharField(max_length=500, blank=True)
    priority = models.IntegerField(default=0, help_text="Higher = shown first")

    class Meta:
        ordering = ['-priority', 'label']

    def __str__(self):
        return f"{self.company.ticker}: {self.label}"


# Keep CompanyScore for backward compatibility during transition
class CompanyScore(models.Model):
    """Simplified snapshot for Phase 1. Will migrate to CompanyValueSnapshot."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='scores')
    score = models.FloatField()
    grade = models.CharField(max_length=5)
    raw_value = models.FloatField()
    reason = models.TextField(blank=True)
    computed_at = models.DateTimeField(auto_now_add=True)
    source_claim_uris = models.JSONField(default=list)

    def __str__(self):
        return f"{self.company.ticker}: {self.grade}"


class BrandMapping(models.Model):
    """Maps product brand names to parent companies.

    Example: brand_name="Häagen-Dazs" -> company=Nestlé
    Example: brand_name="Tide" -> company=Procter & Gamble
    """
    brand_name = models.CharField(max_length=200,
        help_text="Brand name as it appears on products")
    brand_name_normalized = models.CharField(max_length=200, db_index=True,
        help_text="Lowercased, stripped version for matching")
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
        related_name='brand_mappings')
    source = models.CharField(max_length=100, blank=True,
        help_text="Where this mapping came from: manual, wikipedia, open_food_facts")
    confidence = models.FloatField(default=1.0,
        help_text="0-1, how confident we are in this mapping")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['brand_name_normalized', 'company']
        ordering = ['-confidence', 'brand_name']

    def save(self, *args, **kwargs):
        self.brand_name_normalized = self.brand_name.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand_name} -> {self.company.name}"


class BarcodeCache(models.Model):
    """Cache of barcode -> product data from external APIs."""
    barcode = models.CharField(max_length=20, unique=True, db_index=True)
    product_name = models.CharField(max_length=300, blank=True)
    brands = models.CharField(max_length=500, blank=True,
        help_text="Comma-separated brand names from product data")
    owner = models.CharField(max_length=300, blank=True,
        help_text="Owner/manufacturer field from product data")
    categories = models.CharField(max_length=500, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    provider = models.CharField(max_length=50,
        help_text="Which API provided this: open_food_facts, open_beauty_facts, etc.")
    raw_response = models.JSONField(default=dict,
        help_text="Full API response for debugging")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.barcode}: {self.product_name}"


class Product(models.Model):
    """A consumer product available on store shelves.

    Maps a specific product (e.g., "Cheerios Original 18oz") to its parent
    company via brand, with category for suggesting same-category swaps.
    """
    name = models.CharField(max_length=300, help_text="Product name as on shelf")
    brand_name = models.CharField(max_length=200, db_index=True,
        help_text="Brand name, e.g. Cheerios, Doritos, Tide")
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
        related_name='products')
    category = models.CharField(max_length=100, db_index=True,
        help_text="Product category for swap suggestions, e.g. cereal, water, chicken")
    typical_price = models.DecimalField(max_digits=8, decimal_places=2,
        null=True, blank=True, help_text="Typical retail price in USD")
    barcode = models.CharField(max_length=20, blank=True, db_index=True)
    source = models.CharField(max_length=100, blank=True,
        help_text="Where this product data came from")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"
