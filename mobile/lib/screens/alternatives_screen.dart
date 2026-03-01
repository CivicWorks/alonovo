import 'package:flutter/material.dart';
import '../models/scan_result.dart';
import '../widgets/company_card.dart';
import '../widgets/grade_badge.dart';
import '../widgets/value_row.dart';

/// Shows better-rated alternatives in the same sector.
class AlternativesScreen extends StatelessWidget {
  final CompanyInfo company;
  final List<CompanyInfo> alternatives;

  const AlternativesScreen({
    super.key,
    required this.company,
    required this.alternatives,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Better Alternatives'),
        backgroundColor: const Color(0xFF1A5F2A),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Current company summary
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFFEF2F2),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFFFECACA)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'You scanned a product from:',
                          style: TextStyle(
                            fontSize: 12,
                            color: Color(0xFF991B1B),
                          ),
                        ),
                        Text(
                          company.name,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          company.sector,
                          style: const TextStyle(
                            fontSize: 13,
                            color: Color(0xFF666666),
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (company.overallGrade != null)
                    GradeBadge(grade: company.overallGrade!, size: 40),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Animal welfare focus
            _AnimalWelfareComparison(
              company: company,
              alternatives: alternatives,
            ),

            const SizedBox(height: 20),

            // Alternatives list
            Text(
              'Better options in ${company.sector}',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),

            if (alternatives.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: Center(
                  child: Text(
                    'No better-rated alternatives found in this sector.',
                    style: TextStyle(color: Color(0xFF999999)),
                  ),
                ),
              ),

            ...alternatives.map((alt) => CompanyCard(
              company: alt,
              onTap: () => _showCompanyDetail(context, alt),
            )),
          ],
        ),
      ),
    );
  }

  void _showCompanyDetail(BuildContext context, CompanyInfo alt) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        builder: (_, scrollController) {
          final snapshots = List<ValueSnapshot>.from(alt.valueSnapshots)
            ..sort((a, b) {
              if (a.isAnimalWelfare && !b.isAnimalWelfare) return -1;
              if (!a.isAnimalWelfare && b.isAnimalWelfare) return 1;
              return a.valueName.compareTo(b.valueName);
            });

          return ListView(
            controller: scrollController,
            padding: const EdgeInsets.all(16),
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      alt.name,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (alt.overallGrade != null)
                    GradeBadge(grade: alt.overallGrade!, size: 48),
                ],
              ),
              Text(
                '${alt.ticker} - ${alt.sector}',
                style: const TextStyle(
                  fontSize: 14,
                  color: Color(0xFF888888),
                ),
              ),
              const SizedBox(height: 16),
              ...snapshots.map((s) => ValueRow(snapshot: s)),
            ],
          );
        },
      ),
    );
  }
}

class _AnimalWelfareComparison extends StatelessWidget {
  final CompanyInfo company;
  final List<CompanyInfo> alternatives;

  const _AnimalWelfareComparison({
    required this.company,
    required this.alternatives,
  });

  @override
  Widget build(BuildContext context) {
    final companyAW = company.valueSnapshots
        .where((s) => s.isAnimalWelfare)
        .toList();
    if (companyAW.isEmpty) return const SizedBox.shrink();

    final bestAlt = alternatives.isNotEmpty ? alternatives.first : null;
    final altAW = bestAlt?.valueSnapshots
        .where((s) => s.isAnimalWelfare)
        .toList();

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFF0FDF4),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFBBF7D0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.pets, size: 18, color: Color(0xFF1A5F2A)),
              SizedBox(width: 6),
              Text(
                'Animal Welfare Focus',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 15,
                  color: Color(0xFF1A5F2A),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...companyAW.map((snap) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              children: [
                Expanded(child: Text(snap.valueName, style: const TextStyle(fontSize: 13))),
                GradeBadge(grade: snap.grade, size: 24),
                const SizedBox(width: 8),
                Text(company.name, style: const TextStyle(fontSize: 11, color: Color(0xFF999999))),
              ],
            ),
          )),
          if (bestAlt != null && altAW != null && altAW.isNotEmpty) ...[
            const Divider(height: 16),
            Text(
              'vs ${bestAlt.name}:',
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: Color(0xFF1A5F2A),
              ),
            ),
            ...altAW.map((snap) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 2),
              child: Row(
                children: [
                  Expanded(child: Text(snap.valueName, style: const TextStyle(fontSize: 13))),
                  GradeBadge(grade: snap.grade, size: 24),
                  const SizedBox(width: 8),
                  Text(bestAlt.name, style: const TextStyle(fontSize: 11, color: Color(0xFF999999))),
                ],
              ),
            )),
          ],
        ],
      ),
    );
  }
}
