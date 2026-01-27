# Alonovo Data Models

## Core Philosophy

**Claims are the source of truth.** Django models are digested, queryable views of claim data — fully populated for app display, but always pointing back to source claims via URIs.

**LinkedClaims spec (authoritative):** https://identity.foundation/labs-linkedclaims/

## Claim (LinkedClaim Storage)

Immutable facts with provenance. Each claim has a URI and can reference other claims.

```python
class Claim(models.Model):
    """LinkedClaim storage - real fields, not JSONB
    
    Follows: https://identity.foundation/labs-linkedclaims/
    - MUST have uri (id)
    - MUST have subject (URI)
    - MUST be signed (proof)
    - MAY have object (for "A rated B" claims)
    """
    uri = models.CharField(max_length=500, unique=True)
    subject = models.CharField(max_length=500, db_index=True)  # company URI or another claim URI
    object = models.CharField(max_length=500, blank=True)  # optional, for "A rated B" claims
    claim = models.CharField(max_length=100)  # "LOBBYING_SPEND", "CAGE_FREE", "VALIDATED", "ICE_CONTRACT"
    statement = models.TextField(blank=True)
    effective_date = models.DateField(null=True, blank=True)
    source_uri = models.CharField(max_length=500, blank=True)
    how_known = models.CharField(max_length=50)  # FIRST_HAND, WEB_DOCUMENT, RESEARCH, etc.
    date_observed = models.DateField(null=True, blank=True)
    digest_multibase = models.CharField(max_length=200, blank=True)
    
    # For metrics
    amt = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    score = models.FloatField(null=True, blank=True)  # normalized -1 to 1
    
    # For labels/certifications
    label = models.CharField(max_length=100, blank=True)  # "free_range", "b_corp", "cage_free"
    
    # Provenance
    author = models.CharField(max_length=300, blank=True)
    curator = models.CharField(max_length=300, blank=True)
    issuer_id = models.CharField(max_length=300, blank=True)
    issuer_id_type = models.CharField(max_length=20, blank=True)
    proof = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Claim Types

1. **Metric claims** — `amt` + `unit` populated (e.g., lobbying spend $18.8M)
2. **Label claims** — `label` populated (e.g., "cage_free", "b_corp")
3. **Validation claims** — `subject` points to another claim URI, `claim`="VALIDATED" or "DISPUTED"

## Company

```python
class Company(models.Model):
    uri = models.CharField(max_length=500, unique=True)
    ticker = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100)
```

## Value (Admin-Defined Criteria)

```python
class Value(models.Model):
    uri = models.CharField(max_length=500, unique=True)
    name = models.CharField(max_length=100)  # "Lobbying", "Animal Welfare", "ICE Collaboration"
    value_type = models.CharField(max_length=20)  # "metric" | "label" | "categorical_grade"
    description = models.TextField(blank=True)
    methodology_claim_uri = models.CharField(max_length=500, blank=True)
    
    # Platform policy
    default_weight = models.FloatField(default=1.0)
    is_fixed = models.BooleanField(default=False)  # user can't adjust weight
    is_disqualifying = models.BooleanField(default=False)  # F here = F overall
    min_weight = models.FloatField(default=0.0)  # user can't go below this
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)
```

### Value Types

- **metric** — numeric data with thresholds (lobbying spend, emissions)
- **label** — categorical certifications (cage-free, B Corp)
- **categorical_grade** — labels that map to grades (ICE involvement levels)

## ScoringRule

```python
class ScoringRule(models.Model):
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='scoring_rules')
    name = models.CharField(max_length=100)
    version = models.IntegerField(default=1)
    
    # For categorical values — label → grade mapping
    label_grades = models.JSONField(null=True, blank=True)
    # e.g., {
    #   "detention_operator": "F",
    #   "major_contractor": "F",
    #   "minor_contractor": "D",
    #   "passive_involvement": "C",
    #   "financial_ties": "C-"
    # }
    
    # For metric values — thresholds for grading
    thresholds = models.JSONField(null=True, blank=True)
    # e.g., {"A": [0, 1000000], "B": [1000000, 5000000], ...}
    
    methodology_claim_uri = models.CharField(max_length=500, blank=True)
```

## CompanyValueSnapshot (Rollup for Display)

Pre-computed, same for all users. User weights applied at query time.

```python
class CompanyValueSnapshot(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='snapshots')
    value = models.ForeignKey(Value, on_delete=models.CASCADE)
    scoring_rule = models.ForeignKey(ScoringRule, null=True, on_delete=models.SET_NULL)
    
    # Populated based on value_type
    label = models.CharField(max_length=100, blank=True)  # for label/categorical
    raw_value = models.FloatField(null=True, blank=True)  # for metrics
    normalized_score = models.FloatField(null=True, blank=True)  # -1 to 1
    grade = models.CharField(max_length=5, blank=True)
    
    reason = models.TextField(blank=True)
    computed_at = models.DateTimeField(auto_now=True)
    source_claim_uris = models.JSONField(default=list)
    
    # Validation rollup
    validation_count = models.IntegerField(default=0)
    dispute_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['company', 'value']
```

## UserValueWeight (Personal Multipliers)

```python
class UserValueWeight(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='value_weights')
    value = models.ForeignKey(Value, on_delete=models.CASCADE)
    weight = models.FloatField(default=1.0)  # 0 = don't care, 10 = critical
    
    class Meta:
        unique_together = ['user', 'value']
```

## Scoring Logic

```python
def get_company_score(company, user=None):
    snapshots = CompanyValueSnapshot.objects.filter(company=company).select_related('value')
    
    # Check disqualifiers first
    for snap in snapshots:
        if snap.value.is_disqualifying and snap.grade == 'F':
            return {
                'grade': 'F',
                'reason': f'Disqualified: {snap.value.name}',
                'disqualified': True
            }
    
    # Get user weights
    if user and user.is_authenticated:
        user_weights = {w.value_id: w.weight for w in UserValueWeight.objects.filter(user=user)}
    else:
        user_weights = {}
    
    total_score = 0
    total_weight = 0
    
    for snap in snapshots:
        if snap.value.is_fixed:
            w = snap.value.default_weight  # user can't change
        else:
            w = user_weights.get(snap.value_id, snap.value.default_weight)
            w = max(w, snap.value.min_weight)  # enforce floor
        
        if w > 0 and snap.normalized_score is not None:
            total_score += snap.normalized_score * w
            total_weight += w
    
    final = total_score / total_weight if total_weight else 0
    return {
        'score': final,
        'grade': score_to_grade(final),
        'disqualified': False
    }
```

## Data Flow

```
[External Sources] → [Claims] → [Digest/Score] → [CompanyValueSnapshot] → [API]
                                                                              ↓
                                                         [Apply UserValueWeight if logged in]
                                                                              ↓
                                                                      [Display to User]
```

## Platform Stance Example

ICE detention collaboration:

```python
Value(
    name="ICE Collaboration",
    value_type="categorical_grade",
    is_fixed=True,           # user can't zero it out
    is_disqualifying=True,   # detention_operator = auto F overall
    min_weight=1.0,
    default_weight=5.0
)

ScoringRule(
    value=ice_value,
    label_grades={
        "detention_operator": "F",
        "major_contractor": "F",
        "minor_contractor": "D",
        "passive_involvement": "C",
        "financial_ties": "C-"
    }
)
```

Transparent: "Alonovo considers ICE detention collaboration disqualifying. [Learn why]"
