# Alonovo: OAuth + Data Models + Initial Data Import

Complete instructions for setting up OAuth, data models, and initial data import.

---

## 1. OAuth Setup

Install django-allauth with Google provider:

```bash
pip install django-allauth
```

Add to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    # ...existing apps...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_OAUTH_SECRET'),
        }
    }
}

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_AUTO_SIGNUP = True
```

Add to urls.py:
```python
urlpatterns = [
    # ...existing urls...
    path('accounts/', include('allauth.urls')),
]
```

After migrate, create Site in Django admin with domain: alonovo.cooperation.org

Environment variables needed:
- GOOGLE_OAUTH_CLIENT_ID
- GOOGLE_OAUTH_SECRET

Callback URL configured in Google Console: https://alonovo.cooperation.org/accounts/google/login/callback/

---

## 2. Data Models

Create/update `core/models.py`:

```python
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Claim(models.Model):
    """
    LinkedClaim per DIF spec. Immutable source facts.
    """
    uri = models.CharField(max_length=500, primary_key=True)
    subject = models.CharField(max_length=500, db_index=True)
    object = models.CharField(max_length=500, null=True, blank=True)
    claim_type = models.CharField(max_length=100)
    amt = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    source_uri = models.CharField(max_length=1000)
    how_known = models.CharField(max_length=100)
    digest_multibase = models.CharField(max_length=200, null=True, blank=True)
    proof = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self._state.adding:
            super().save(*args, **kwargs)
        else:
            raise ValueError("Claims are immutable and cannot be updated")

    def __str__(self):
        return self.uri


class Company(models.Model):
    uri = models.CharField(max_length=500, primary_key=True)
    ticker = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=300)
    sector = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Value(models.Model):
    VALUE_TYPES = [
        ('metric', 'Metric'),
        ('label', 'Label'),
        ('categorical_grade', 'Categorical Grade'),
    ]

    slug = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    value_type = models.CharField(max_length=20, choices=VALUE_TYPES)
    is_fixed = models.BooleanField(default=False)
    is_disqualifying = models.BooleanField(default=False)
    min_weight = models.IntegerField(default=0)
    card_display_template = models.CharField(max_length=200, null=True, blank=True)
    card_icon = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ScoringRule(models.Model):
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='scoring_rules')
    version = models.IntegerField()
    config = models.JSONField()
    effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['value', 'version']]
        ordering = ['-version']

    def __str__(self):
        return f"{self.value.slug} v{self.version}"


class CompanyValueSnapshot(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='snapshots')
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='snapshots')
    score = models.FloatField()
    grade = models.CharField(max_length=10)
    claim_uris = models.JSONField(default=list)
    validation_count = models.IntegerField(default=0)
    dispute_count = models.IntegerField(default=0)
    highlight_on_card = models.BooleanField(default=False)
    highlight_priority = models.IntegerField(default=0)
    display_text = models.CharField(max_length=300, null=True, blank=True)
    display_icon = models.CharField(max_length=50, null=True, blank=True)
    computed_at = models.DateTimeField(auto_now=True)
    scoring_rule_version = models.IntegerField()

    class Meta:
        unique_together = [['company', 'value']]

    def __str__(self):
        return f"{self.company.name} - {self.value.name}: {self.grade}"


class UserValueWeight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='value_weights')
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='user_weights')
    weight = models.IntegerField(default=5)  # 0-10

    class Meta:
        unique_together = [['user', 'value']]

    def __str__(self):
        return f"{self.user.username} - {self.value.name}: {self.weight}"
```

---

## 3. Admin Registration

Create/update `core/admin.py`:

```python
from django.contrib import admin
from .models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, UserValueWeight


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['uri', 'subject', 'claim_type', 'amt', 'label', 'effective_date']
    list_filter = ['claim_type', 'how_known']
    search_fields = ['uri', 'subject', 'source_uri']
    readonly_fields = ['uri', 'subject', 'object', 'claim_type', 'amt', 'unit', 'label', 
                       'effective_date', 'source_uri', 'how_known', 'digest_multibase', 
                       'proof', 'created_at']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['uri', 'name', 'ticker', 'sector']
    list_filter = ['sector']
    search_fields = ['uri', 'name', 'ticker']


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'value_type', 'is_fixed', 'is_disqualifying']
    list_filter = ['value_type', 'is_fixed', 'is_disqualifying']


@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = ['value', 'version', 'effective_date']
    list_filter = ['value']


@admin.register(CompanyValueSnapshot)
class CompanyValueSnapshotAdmin(admin.ModelAdmin):
    list_display = ['company', 'value', 'grade', 'score', 'highlight_on_card', 'computed_at']
    list_filter = ['value', 'grade', 'highlight_on_card']
    search_fields = ['company__name']


@admin.register(UserValueWeight)
class UserValueWeightAdmin(admin.ModelAdmin):
    list_display = ['user', 'value', 'weight']
    list_filter = ['value']
```

---

## 4. Initial Data Import Command

Create `core/management/commands/import_initial_data.py`:

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot


class Command(BaseCommand):
    help = "Import initial values, scoring rules, companies, claims, and compute snapshots"

    def handle(self, *args, **options):
        self.stdout.write("Creating Values...")
        self.create_values()
        
        self.stdout.write("Creating ScoringRules...")
        self.create_scoring_rules()
        
        self.stdout.write("Importing companies and claims...")
        self.import_companies_and_claims()
        
        self.stdout.write("Computing snapshots...")
        self.compute_snapshots()
        
        self.stdout.write(self.style.SUCCESS("Done!"))

    def create_values(self):
        values_data = [
            {
                'slug': 'cage_free_eggs',
                'name': 'Cage-Free Egg Commitment',
                'description': 'Progress toward 100% cage-free egg sourcing',
                'value_type': 'metric',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': '{amt}% cage-free',
                'card_icon': 'egg',
            },
            {
                'slug': 'farm_animal_welfare',
                'name': 'Farm Animal Welfare Rating',
                'description': 'BBFAW tier rating (1-6, lower is better)',
                'value_type': 'categorical_grade',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'BBFAW Tier {label}',
                'card_icon': 'cow',
            },
            {
                'slug': 'ice_contracts',
                'name': 'ICE/CBP Contracts',
                'description': 'Active contracts with Immigration and Customs Enforcement or Customs and Border Protection',
                'value_type': 'metric',
                'is_fixed': True,
                'is_disqualifying': False,
                'min_weight': 1,
                'card_display_template': 'ICE contracts: ${amt}M',
                'card_icon': 'warning',
            },
            {
                'slug': 'ice_detention',
                'name': 'ICE Detention Operations',
                'description': 'Operates or directly supports immigrant detention facilities',
                'value_type': 'label',
                'is_fixed': True,
                'is_disqualifying': True,
                'min_weight': 5,
                'card_display_template': 'Detention operator',
                'card_icon': 'alert',
            },
        ]
        
        for data in values_data:
            Value.objects.update_or_create(slug=data['slug'], defaults=data)

    def create_scoring_rules(self):
        # Cage-free scoring
        Value.objects.get(slug='cage_free_eggs')
        ScoringRule.objects.update_or_create(
            value_id='cage_free_eggs',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold',
                    'thresholds': [
                        {'min': 95, 'grade': 'A', 'score': 1.0},
                        {'min': 80, 'grade': 'B', 'score': 0.6},
                        {'min': 50, 'grade': 'C', 'score': 0.2},
                        {'min': 25, 'grade': 'D', 'score': -0.2},
                        {'min': 0, 'grade': 'F', 'score': -1.0},
                    ]
                }
            }
        )

        # BBFAW tier scoring
        ScoringRule.objects.update_or_create(
            value_id='farm_animal_welfare',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'categorical',
                    'mapping': {
                        '1': {'grade': 'A', 'score': 1.0},
                        '2': {'grade': 'A-', 'score': 0.85},
                        '3': {'grade': 'B', 'score': 0.6},
                        '4': {'grade': 'C', 'score': 0.2},
                        '5': {'grade': 'D', 'score': -0.4},
                        '6': {'grade': 'F', 'score': -1.0},
                    }
                }
            }
        )

        # ICE contracts scoring
        ScoringRule.objects.update_or_create(
            value_id='ice_contracts',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold_inverse',  # higher is worse
                    'thresholds': [
                        {'min': 50, 'grade': 'F', 'score': -1.0},
                        {'min': 10, 'grade': 'D', 'score': -0.6},
                        {'min': 1, 'grade': 'C', 'score': -0.2},
                        {'min': 0.1, 'grade': 'C+', 'score': 0.0},
                        {'min': 0, 'grade': 'A', 'score': 1.0},
                    ]
                }
            }
        )

        # ICE detention scoring
        ScoringRule.objects.update_or_create(
            value_id='ice_detention',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'label',
                    'mapping': {
                        'detention_operator': {'grade': 'F', 'score': -1.0},
                        'major_contractor': {'grade': 'F', 'score': -1.0},
                        'none': {'grade': 'A', 'score': 1.0},
                    }
                }
            }
        )

    def import_companies_and_claims(self):
        # BBFAW Data (source: https://www.bbfaw.com/media/2190/bbfaw-2024-report.pdf)
        bbfaw_data = [
            ('marks-and-spencer', 'Marks & Spencer', 'MKS.L', 'Retail', '2'),
            ('waitrose', 'Waitrose', None, 'Retail', '2'),
            ('premier-foods', 'Premier Foods', 'PFD.L', 'Food Manufacturing', '2'),
            ('greggs', 'Greggs', 'GRG.L', 'Restaurants', '2'),
            ('mcdonalds', "McDonald's", 'MCD', 'Restaurants', '5'),
            ('tyson-foods', 'Tyson Foods', 'TSN', 'Food Manufacturing', '5'),
            ('amazon-whole-foods', 'Amazon/Whole Foods', 'AMZN', 'Retail', '5'),
            ('dominos-pizza', "Domino's Pizza", 'DPZ', 'Restaurants', '5'),
            ('nestle', 'Nestlé', 'NESN.SW', 'Food Manufacturing', '5'),
            ('walmart', 'Walmart', 'WMT', 'Retail', '5'),
            ('tesco', 'Tesco', 'TSCO.L', 'Retail', '4'),
            ('costco', 'Costco', 'COST', 'Retail', '5'),
            ('kroger', 'Kroger', 'KR', 'Retail', '5'),
        ]

        for slug, name, ticker, sector, tier in bbfaw_data:
            uri = f'urn:company:{slug}'
            Company.objects.update_or_create(
                uri=uri,
                defaults={'name': name, 'ticker': ticker, 'sector': sector}
            )
            
            claim_uri = f'urn:bbfaw:2024:{slug}:tier'
            try:
                Claim.objects.create(
                    uri=claim_uri,
                    subject=uri,
                    claim_type='FARM_WELFARE_TIER',
                    label=tier,
                    effective_date='2024-04-25',
                    source_uri='https://www.bbfaw.com/media/2190/bbfaw-2024-report.pdf',
                    how_known='official_report'
                )
            except ValueError:
                pass  # Claim already exists

        # EggTrack Data (source: https://www.eggtrack.com/en/)
        eggtrack_data = [
            ('danone', 'Danone', 'BN.PA', 'Food Manufacturing', 100),
            ('barilla', 'Barilla', None, 'Food Manufacturing', 100),
            ('mcdonalds', "McDonald's", 'MCD', 'Restaurants', 33),
            ('walmart', 'Walmart', 'WMT', 'Retail', 14),
            ('raleys', "Raley's", None, 'Retail', 100),
            ('sprouts', 'Sprouts Farmers Market', 'SFM', 'Retail', 100),
            ('hershey', 'The Hershey Company', 'HSY', 'Food Manufacturing', 100),
            ('kraft-heinz', 'Kraft Heinz', 'KHC', 'Food Manufacturing', 85),
            ('kfc-europe', 'KFC Europe', None, 'Restaurants', 100),
        ]

        for slug, name, ticker, sector, pct in eggtrack_data:
            uri = f'urn:company:{slug}'
            Company.objects.update_or_create(
                uri=uri,
                defaults={'name': name, 'ticker': ticker, 'sector': sector}
            )
            
            claim_uri = f'urn:eggtrack:2024:{slug}:cagefree'
            try:
                Claim.objects.create(
                    uri=claim_uri,
                    subject=uri,
                    claim_type='CAGE_FREE_PERCENT',
                    amt=Decimal(str(pct)),
                    unit='percent',
                    effective_date='2024-01-01',
                    source_uri='https://www.eggtrack.com/en/',
                    how_known='official_tracker'
                )
            except ValueError:
                pass

        # ICE Contracts Data (source: Fortune June 2025, USASpending.gov)
        ice_contracts_data = [
            ('dell', 'Dell', 'DELL', 'Technology', Decimal('18.8')),
            ('motorola-solutions', 'Motorola Solutions', 'MSI', 'Technology', Decimal('15.6')),
            ('l3harris', 'L3Harris', 'LHX', 'Defense', Decimal('4.4')),
            ('comcast', 'Comcast', 'CMCSA', 'Telecommunications', Decimal('0.061')),
            ('ecolab', 'Ecolab', 'ECL', 'Manufacturing', Decimal('0.137')),
            ('ups', 'UPS', 'UPS', 'Logistics', Decimal('0.061')),
            ('sosi', 'SOSi', None, 'Defense', Decimal('123')),
            ('gravitas', 'Gravitas Investigations', None, 'Services', Decimal('32')),
            ('government-support-services', 'Government Support Services', None, 'Services', Decimal('55')),
        ]

        for slug, name, ticker, sector, amt in ice_contracts_data:
            uri = f'urn:company:{slug}'
            Company.objects.update_or_create(
                uri=uri,
                defaults={'name': name, 'ticker': ticker, 'sector': sector}
            )
            
            claim_uri = f'urn:usaspending:2025:{slug}:ice'
            try:
                Claim.objects.create(
                    uri=claim_uri,
                    subject=uri,
                    claim_type='ICE_CONTRACT',
                    amt=amt,
                    unit='million_usd',
                    effective_date='2025-06-01',
                    source_uri='https://www.usaspending.gov/',
                    how_known='federal_spending_data'
                )
            except ValueError:
                pass

        # ICE Detention Operators (source: The Intercept Dec 2025)
        detention_data = [
            ('geo-group', 'GEO Group', 'GEO', 'Private Prisons'),
            ('corecivic', 'CoreCivic', 'CXW', 'Private Prisons'),
        ]

        for slug, name, ticker, sector in detention_data:
            uri = f'urn:company:{slug}'
            Company.objects.update_or_create(
                uri=uri,
                defaults={'name': name, 'ticker': ticker, 'sector': sector}
            )
            
            claim_uri = f'urn:ice:2025:{slug}:detention'
            try:
                Claim.objects.create(
                    uri=claim_uri,
                    subject=uri,
                    claim_type='ICE_DETENTION_OPERATOR',
                    label='detention_operator',
                    effective_date='2025-12-01',
                    source_uri='https://theintercept.com/2025/12/23/ice-bounty-hunters-track-immigrant-surveillance/',
                    how_known='investigative_journalism'
                )
            except ValueError:
                pass

    def compute_snapshots(self):
        """Compute CompanyValueSnapshot for each company/value pair with claims."""
        
        for company in Company.objects.all():
            claims = Claim.objects.filter(subject=company.uri)
            
            # BBFAW tier claims
            bbfaw_claims = claims.filter(claim_type='FARM_WELFARE_TIER')
            if bbfaw_claims.exists():
                claim = bbfaw_claims.first()
                rule = ScoringRule.objects.get(value_id='farm_animal_welfare', version=1)
                mapping = rule.config['mapping'].get(claim.label, {'grade': 'F', 'score': -1.0})
                
                CompanyValueSnapshot.objects.update_or_create(
                    company=company,
                    value_id='farm_animal_welfare',
                    defaults={
                        'score': mapping['score'],
                        'grade': mapping['grade'],
                        'claim_uris': [claim.uri],
                        'highlight_on_card': True,
                        'highlight_priority': 1,
                        'display_text': f"BBFAW Tier {claim.label}",
                        'display_icon': 'cow',
                        'scoring_rule_version': 1,
                    }
                )

            # Cage-free claims
            cage_claims = claims.filter(claim_type='CAGE_FREE_PERCENT')
            if cage_claims.exists():
                claim = cage_claims.first()
                rule = ScoringRule.objects.get(value_id='cage_free_eggs', version=1)
                
                grade = 'F'
                score = -1.0
                for threshold in rule.config['thresholds']:
                    if claim.amt >= threshold['min']:
                        grade = threshold['grade']
                        score = threshold['score']
                        break
                
                CompanyValueSnapshot.objects.update_or_create(
                    company=company,
                    value_id='cage_free_eggs',
                    defaults={
                        'score': score,
                        'grade': grade,
                        'claim_uris': [claim.uri],
                        'highlight_on_card': True,
                        'highlight_priority': 2,
                        'display_text': f"{claim.amt}% cage-free",
                        'display_icon': 'egg',
                        'scoring_rule_version': 1,
                    }
                )

            # ICE contract claims
            ice_claims = claims.filter(claim_type='ICE_CONTRACT')
            if ice_claims.exists():
                claim = ice_claims.first()
                rule = ScoringRule.objects.get(value_id='ice_contracts', version=1)
                
                grade = 'A'
                score = 1.0
                for threshold in rule.config['thresholds']:
                    if float(claim.amt) >= threshold['min']:
                        grade = threshold['grade']
                        score = threshold['score']
                        break
                
                CompanyValueSnapshot.objects.update_or_create(
                    company=company,
                    value_id='ice_contracts',
                    defaults={
                        'score': score,
                        'grade': grade,
                        'claim_uris': [claim.uri],
                        'highlight_on_card': True,
                        'highlight_priority': 0,  # highest priority
                        'display_text': f"ICE contracts: ${claim.amt}M",
                        'display_icon': 'warning',
                        'scoring_rule_version': 1,
                    }
                )

            # ICE detention claims
            detention_claims = claims.filter(claim_type='ICE_DETENTION_OPERATOR')
            if detention_claims.exists():
                claim = detention_claims.first()
                
                CompanyValueSnapshot.objects.update_or_create(
                    company=company,
                    value_id='ice_detention',
                    defaults={
                        'score': -1.0,
                        'grade': 'F',
                        'claim_uris': [claim.uri],
                        'highlight_on_card': True,
                        'highlight_priority': 0,
                        'display_text': 'ICE detention operator',
                        'display_icon': 'alert',
                        'scoring_rule_version': 1,
                    }
                )
```

---

## 5. Header UI Changes (Svelte)

Update header component to include:

```svelte
<script>
    export let user = null;  // from Django context or API
</script>

<header>
    <div class="logo">
        <a href="/">Alonovo</a>
    </div>
    
    <nav class="auth">
        {#if user}
            <span class="user-email">{user.email}</span>
            {#if user.is_staff}
                <a href="/admin/" class="admin-link">Admin</a>
            {/if}
            <a href="/accounts/logout/" class="sign-out">Sign out</a>
        {:else}
            <a href="/accounts/google/login/" class="sign-in">Sign in</a>
        {/if}
    </nav>
</header>

<style>
    .auth {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.875rem;
    }
    
    .sign-in, .sign-out, .admin-link {
        color: #666;
        text-decoration: none;
    }
    
    .sign-in:hover, .sign-out:hover, .admin-link:hover {
        color: #333;
    }
    
    .user-email {
        color: #999;
    }
</style>
```

---

## 6. API Endpoint for User Context

Add to views.py:

```python
from django.http import JsonResponse

def user_context(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'email': request.user.email,
            'is_staff': request.user.is_staff,
        })
    return JsonResponse({'authenticated': False})
```

Add to urls.py:
```python
path('api/user/', views.user_context, name='user_context'),
```

---

## 7. Run Commands

```bash
# Install allauth
pip install django-allauth

# Create migrations and migrate
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Import initial data
python manage.py import_initial_data

# In Django admin, set Site domain to alonovo.cooperation.org
```

---

## 8. Environment Variables

Add to .env or server environment:

```
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_SECRET=your-client-secret
```

---

## Data Sources Reference

### Animal Welfare
- **BBFAW**: https://www.bbfaw.com/media/2190/bbfaw-2024-report.pdf
- **EggTrack**: https://www.eggtrack.com/en/

### ICE Collaboration
- **USASpending**: https://www.usaspending.gov/
- **Fortune 500 ICE contracts**: https://fortune.com/2025/06/26/fortune-500-companies-active-contracts-immigration-and-customs-enforcement-ice/
- **ICE bounty hunting**: https://theintercept.com/2025/12/23/ice-bounty-hunters-track-immigrant-surveillance/
