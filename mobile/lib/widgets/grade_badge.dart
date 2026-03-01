import 'package:flutter/material.dart';
import '../config.dart';

/// Circular grade badge (A-F) with color coding.
class GradeBadge extends StatelessWidget {
  final String grade;
  final double size;

  const GradeBadge({super.key, required this.grade, this.size = 48});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: _gradeColor(grade),
        shape: BoxShape.circle,
      ),
      alignment: Alignment.center,
      child: Text(
        grade,
        style: TextStyle(
          color: grade == 'C' ? const Color(0xFF1A1A1A) : Colors.white,
          fontWeight: FontWeight.bold,
          fontSize: size * 0.45,
        ),
      ),
    );
  }

  static Color _gradeColor(String grade) {
    switch (grade.isNotEmpty ? grade[0] : '') {
      case 'A':
        return const Color(Config.gradeAColor);
      case 'B':
        return const Color(Config.gradeBColor);
      case 'C':
        return const Color(Config.gradeCColor);
      case 'D':
        return const Color(Config.gradeDColor);
      case 'F':
        return const Color(Config.gradeFColor);
      default:
        return Colors.grey;
    }
  }
}
