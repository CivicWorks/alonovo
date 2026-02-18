/// Full response from POST /api/scan/
class ScanResult {
  final String barcode;
  final ProductInfo? product;
  final CompanyInfo? company;
  final List<CompanyInfo> alternatives;
  final double matchConfidence;
  final String matchMethod;

  ScanResult({
    required this.barcode,
    this.product,
    this.company,
    required this.alternatives,
    required this.matchConfidence,
    required this.matchMethod,
  });

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    return ScanResult(
      barcode: json['barcode'] ?? '',
      product: json['product'] != null
          ? ProductInfo.fromJson(json['product'])
          : null,
      company: json['company'] != null
          ? CompanyInfo.fromJson(json['company'])
          : null,
      alternatives: (json['alternatives'] as List? ?? [])
          .map((a) => CompanyInfo.fromJson(a))
          .toList(),
      matchConfidence: (json['match_confidence'] ?? 0).toDouble(),
      matchMethod: json['match_method'] ?? 'unknown',
    );
  }
}

class ProductInfo {
  final String name;
  final String brands;
  final String categories;
  final String imageUrl;
  final String ecoscoreGrade;
  final String provider;

  ProductInfo({
    required this.name,
    required this.brands,
    required this.categories,
    required this.imageUrl,
    required this.ecoscoreGrade,
    required this.provider,
  });

  factory ProductInfo.fromJson(Map<String, dynamic> json) {
    return ProductInfo(
      name: json['name'] ?? '',
      brands: json['brands'] ?? '',
      categories: json['categories'] ?? '',
      imageUrl: json['image_url'] ?? '',
      ecoscoreGrade: json['ecoscore_grade'] ?? '',
      provider: json['provider'] ?? '',
    );
  }
}

class CompanyInfo {
  final int id;
  final String uri;
  final String ticker;
  final String name;
  final String sector;
  final String? overallGrade;
  final List<ValueSnapshot> valueSnapshots;
  final List<Badge> badges;

  CompanyInfo({
    required this.id,
    required this.uri,
    required this.ticker,
    required this.name,
    required this.sector,
    this.overallGrade,
    required this.valueSnapshots,
    required this.badges,
  });

  factory CompanyInfo.fromJson(Map<String, dynamic> json) {
    return CompanyInfo(
      id: json['id'] ?? 0,
      uri: json['uri'] ?? '',
      ticker: json['ticker'] ?? '',
      name: json['name'] ?? '',
      sector: json['sector'] ?? '',
      overallGrade: json['overall_grade'],
      valueSnapshots: (json['value_snapshots'] as List? ?? [])
          .map((s) => ValueSnapshot.fromJson(s))
          .toList(),
      badges: (json['badges'] as List? ?? [])
          .map((b) => Badge.fromJson(b))
          .toList(),
    );
  }
}

class ValueSnapshot {
  final String valueSlug;
  final String valueName;
  final double score;
  final String grade;
  final String displayText;
  final String displayIcon;
  final String computedAt;

  ValueSnapshot({
    required this.valueSlug,
    required this.valueName,
    required this.score,
    required this.grade,
    required this.displayText,
    required this.displayIcon,
    required this.computedAt,
  });

  factory ValueSnapshot.fromJson(Map<String, dynamic> json) {
    return ValueSnapshot(
      valueSlug: json['value_slug'] ?? '',
      valueName: json['value_name'] ?? '',
      score: (json['score'] ?? 0).toDouble(),
      grade: json['grade'] ?? '',
      displayText: json['display_text'] ?? '',
      displayIcon: json['display_icon'] ?? '',
      computedAt: json['computed_at'] ?? '',
    );
  }

  /// Whether this is an animal welfare value.
  bool get isAnimalWelfare => const {
    'farm_animal_welfare',
    'cage_free_eggs',
    'cruelty_free',
  }.contains(valueSlug);
}

class Badge {
  final String label;
  final String type;
  final int priority;

  Badge({
    required this.label,
    required this.type,
    required this.priority,
  });

  factory Badge.fromJson(Map<String, dynamic> json) {
    return Badge(
      label: json['label'] ?? '',
      type: json['type'] ?? 'neutral',
      priority: json['priority'] ?? 0,
    );
  }
}
