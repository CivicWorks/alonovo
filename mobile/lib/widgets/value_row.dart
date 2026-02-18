import 'package:flutter/material.dart';
import '../models/scan_result.dart';
import 'grade_badge.dart';

/// A single value rating row (e.g., "Farm Animal Welfare: B").
class ValueRow extends StatelessWidget {
  final ValueSnapshot snapshot;

  const ValueRow({super.key, required this.snapshot});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          if (snapshot.isAnimalWelfare)
            const Padding(
              padding: EdgeInsets.only(right: 8),
              child: Icon(Icons.pets, size: 18, color: Color(0xFF22C55E)),
            ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  snapshot.valueName,
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                    color: snapshot.isAnimalWelfare
                        ? const Color(0xFF1A5F2A)
                        : const Color(0xFF333333),
                  ),
                ),
                if (snapshot.displayText.isNotEmpty)
                  Text(
                    snapshot.displayText,
                    style: const TextStyle(fontSize: 12, color: Color(0xFF666666)),
                  ),
              ],
            ),
          ),
          GradeBadge(grade: snapshot.grade, size: 32),
        ],
      ),
    );
  }
}
