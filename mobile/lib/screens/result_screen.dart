import 'package:flutter/material.dart';
import '../models/scan_result.dart';
import '../widgets/grade_badge.dart';
import '../widgets/value_row.dart';
import 'alternatives_screen.dart';
import 'scanner_screen.dart';

/// Shows company ratings after a successful barcode scan.
class ResultScreen extends StatelessWidget {
  final ScanResult result;

  const ResultScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final product = result.product!;
    final company = result.company!;

    // Sort snapshots: animal welfare first, then alphabetical
    final snapshots = List<ValueSnapshot>.from(company.valueSnapshots)
      ..sort((a, b) {
        if (a.isAnimalWelfare && !b.isAnimalWelfare) return -1;
        if (!a.isAnimalWelfare && b.isAnimalWelfare) return 1;
        return a.valueName.compareTo(b.valueName);
      });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Product Rating'),
        backgroundColor: const Color(0xFF1A5F2A),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code_scanner),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const ScannerScreen()),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Product info
            _ProductHeader(product: product),
            const SizedBox(height: 16),

            // Match info
            if (result.matchConfidence < 0.8)
              Container(
                padding: const EdgeInsets.all(8),
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF3C7),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Match confidence: ${(result.matchConfidence * 100).toInt()}% (${result.matchMethod.replaceAll("_", " ")})',
                  style: const TextStyle(fontSize: 12, color: Color(0xFF92400E)),
                ),
              ),

            // Company header with grade
            _CompanyHeader(company: company),
            const SizedBox(height: 16),

            // Badges
            if (company.badges.isNotEmpty) ...[
              Wrap(
                spacing: 6,
                runSpacing: 4,
                children: company.badges.map((badge) {
                  return Chip(
                    label: Text(badge.label),
                    labelStyle: const TextStyle(fontSize: 11),
                    padding: EdgeInsets.zero,
                    visualDensity: VisualDensity.compact,
                    backgroundColor: badge.type == 'positive'
                        ? const Color(0xFFDCFCE7)
                        : badge.type == 'negative'
                            ? const Color(0xFFFEE2E2)
                            : const Color(0xFFF3F4F6),
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
            ],

            // Value ratings
            if (snapshots.isNotEmpty) ...[
              const Text(
                'Value Ratings',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1A1A1A),
                ),
              ),
              const SizedBox(height: 8),
              ...snapshots.map((s) => ValueRow(snapshot: s)),
            ],

            // No ratings
            if (snapshots.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: Center(
                  child: Text(
                    'No detailed ratings available yet for this company.',
                    style: TextStyle(color: Color(0xFF999999)),
                  ),
                ),
              ),

            const SizedBox(height: 24),

            // Alternatives button
            if (result.alternatives.isNotEmpty)
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => AlternativesScreen(
                          company: company,
                          alternatives: result.alternatives,
                        ),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1A5F2A),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: Text(
                    'See ${result.alternatives.length} Better Alternative${result.alternatives.length == 1 ? "" : "s"}',
                    style: const TextStyle(fontSize: 16),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _ProductHeader extends StatelessWidget {
  final ProductInfo product;
  const _ProductHeader({required this.product});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (product.imageUrl.isNotEmpty)
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.network(
              product.imageUrl,
              width: 80,
              height: 80,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => const SizedBox(
                width: 80,
                height: 80,
                child: Icon(Icons.image_not_supported, color: Colors.grey),
              ),
            ),
          ),
        if (product.imageUrl.isNotEmpty) const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                product.name,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              if (product.brands.isNotEmpty)
                Text(
                  product.brands,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Color(0xFF666666),
                  ),
                ),
              if (product.categories.isNotEmpty)
                Text(
                  product.categories,
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF999999),
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
            ],
          ),
        ),
      ],
    );
  }
}

class _CompanyHeader extends StatelessWidget {
  final CompanyInfo company;
  const _CompanyHeader({required this.company});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFAFAFA),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  company.name,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '${company.ticker} - ${company.sector}',
                  style: const TextStyle(
                    fontSize: 14,
                    color: Color(0xFF888888),
                  ),
                ),
              ],
            ),
          ),
          if (company.overallGrade != null)
            GradeBadge(grade: company.overallGrade!, size: 56),
        ],
      ),
    );
  }
}
