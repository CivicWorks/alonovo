import 'package:flutter/material.dart';
import '../models/scan_result.dart';
import 'grade_badge.dart';

/// Summary card for a company (used in alternatives list).
class CompanyCard extends StatelessWidget {
  final CompanyInfo company;
  final VoidCallback? onTap;

  const CompanyCard({super.key, required this.company, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      company.name,
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${company.ticker} - ${company.sector}',
                      style: const TextStyle(
                        fontSize: 13,
                        color: Color(0xFF888888),
                      ),
                    ),
                    if (company.badges.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 6),
                        child: Wrap(
                          spacing: 4,
                          children: company.badges.take(3).map((badge) {
                            return Chip(
                              label: Text(badge.label),
                              labelStyle: const TextStyle(fontSize: 10),
                              padding: EdgeInsets.zero,
                              visualDensity: VisualDensity.compact,
                              backgroundColor: _badgeColor(badge.type),
                            );
                          }).toList(),
                        ),
                      ),
                  ],
                ),
              ),
              if (company.overallGrade != null)
                GradeBadge(grade: company.overallGrade!, size: 44),
            ],
          ),
        ),
      ),
    );
  }

  Color _badgeColor(String type) {
    switch (type) {
      case 'positive':
        return const Color(0xFFDCFCE7);
      case 'negative':
        return const Color(0xFFFEE2E2);
      default:
        return const Color(0xFFF3F4F6);
    }
  }
}
