import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../services/api_service.dart';
import 'result_screen.dart';
import 'not_found_screen.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final MobileScannerController _controller = MobileScannerController();
  final ApiService _api = ApiService();
  bool _processing = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onBarcodeDetected(BarcodeCapture capture) {
    if (_processing) return;
    final barcode = capture.barcodes.firstOrNull?.rawValue;
    if (barcode == null || barcode.isEmpty) return;

    setState(() => _processing = true);
    _lookupBarcode(barcode);
  }

  Future<void> _lookupBarcode(String barcode) async {
    try {
      final result = await _api.scanBarcode(barcode);

      if (!mounted) return;

      if (result.company != null) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => ResultScreen(result: result),
          ),
        );
      } else {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => NotFoundScreen(result: result),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _processing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Barcode'),
        backgroundColor: const Color(0xFF1A5F2A),
        foregroundColor: Colors.white,
      ),
      body: Stack(
        children: [
          MobileScanner(
            controller: _controller,
            onDetect: _onBarcodeDetected,
          ),
          // Scan area overlay
          Center(
            child: Container(
              width: 280,
              height: 160,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.white, width: 2),
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          // Instructions
          Positioned(
            bottom: 80,
            left: 0,
            right: 0,
            child: Text(
              _processing
                  ? 'Looking up product...'
                  : 'Point camera at a barcode',
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          // Loading indicator
          if (_processing)
            const Center(
              child: CircularProgressIndicator(color: Colors.white),
            ),
        ],
      ),
    );
  }
}
