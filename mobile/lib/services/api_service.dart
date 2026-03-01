import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';
import '../models/scan_result.dart';

/// HTTP client for the Alonovo backend API.
class ApiService {
  final String baseUrl;

  ApiService({this.baseUrl = Config.apiBaseUrl});

  /// Scan a barcode and get product + company + alternatives.
  Future<ScanResult> scanBarcode(String barcode) async {
    final response = await http.post(
      Uri.parse('$baseUrl/scan/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'barcode': barcode}),
    );

    if (response.statusCode != 200) {
      throw ApiException('Scan failed: ${response.statusCode}');
    }

    return ScanResult.fromJson(jsonDecode(response.body));
  }

  /// Get alternatives for a company by ticker.
  Future<AlternativesResult> getAlternatives(String ticker) async {
    final response = await http.get(
      Uri.parse('$baseUrl/alternatives/$ticker/'),
    );

    if (response.statusCode != 200) {
      throw ApiException('Failed to load alternatives: ${response.statusCode}');
    }

    return AlternativesResult.fromJson(jsonDecode(response.body));
  }
}

class AlternativesResult {
  final CompanyInfo company;
  final List<CompanyInfo> alternatives;
  final Map<String, dynamic> animalWelfareHighlight;

  AlternativesResult({
    required this.company,
    required this.alternatives,
    required this.animalWelfareHighlight,
  });

  factory AlternativesResult.fromJson(Map<String, dynamic> json) {
    return AlternativesResult(
      company: CompanyInfo.fromJson(json['company']),
      alternatives: (json['alternatives'] as List? ?? [])
          .map((a) => CompanyInfo.fromJson(a))
          .toList(),
      animalWelfareHighlight:
          json['animal_welfare_highlight'] as Map<String, dynamic>? ?? {},
    );
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}
