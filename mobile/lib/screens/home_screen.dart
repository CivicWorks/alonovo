import 'package:flutter/material.dart';
import 'scanner_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.eco,
                  size: 80,
                  color: Color(0xFF1A5F2A),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Alonovo',
                  style: TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1A1A1A),
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Know before you buy.\nKnow before you invest.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 16,
                    color: Color(0xFF666666),
                  ),
                ),
                const SizedBox(height: 48),
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const ScannerScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.qr_code_scanner, size: 28),
                    label: const Text(
                      'Scan Product',
                      style: TextStyle(fontSize: 18),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF1A5F2A),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 48),
                const Text(
                  'Scan a product barcode to see the company\'s\nethical ratings and better alternatives',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 13,
                    color: Color(0xFF999999),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
