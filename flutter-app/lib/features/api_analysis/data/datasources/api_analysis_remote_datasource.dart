import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../domain/entities/api_analysis_entity.dart';
import 'api_analysis_datasource.dart';

/// Remote data source for API analysis
class ApiAnalysisRemoteDataSource implements ApiAnalysisDataSource {
  final String _baseUrl;

  ApiAnalysisRemoteDataSource({String? baseUrl})
    : _baseUrl = baseUrl ?? 'http://localhost:8001/api/v1';

  @override
  Future<Map<String, dynamic>> analyzeApiEndpoint(String endpoint) async {
    try {
      final uri = Uri.parse('$_baseUrl/analyze');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'endpoint': endpoint,
          'analysis_type': 'security',
          'include_performance': false,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          return data['data'];
        } else {
          throw Exception(data['error'] ?? 'Analysis failed');
        }
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } on SocketException {
      throw Exception(
        'Unable to connect to API Analysis Service. '
        'Make sure the service is running on $_baseUrl',
      );
    } catch (e) {
      throw Exception('Failed to analyze API endpoint: $e');
    }
  }

  @override
  Future<List<Map<String, dynamic>>> getAnalysisHistory() async {
    try {
      final uri = Uri.parse('$_baseUrl/analysis/history?page=1&per_page=20');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return (data['analyses'] as List).cast<Map<String, dynamic>>();
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } on SocketException {
      throw Exception('Unable to connect to API Analysis Service');
    } catch (e) {
      throw Exception('Failed to get analysis history: $e');
    }
  }

  @override
  Future<Map<String, dynamic>?> getAnalysisById(String id) async {
    try {
      final uri = Uri.parse('$_baseUrl/analysis/$id');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 404) {
        return null;
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } on SocketException {
      throw Exception('Unable to connect to API Analysis Service');
    } catch (e) {
      throw Exception('Failed to get analysis by ID: $e');
    }
  }

  /// Get analysis statistics
  Future<Map<String, dynamic>> getAnalysisStatistics() async {
    try {
      final uri = Uri.parse('$_baseUrl/stats');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } on SocketException {
      throw Exception('Unable to connect to API Analysis Service');
    } catch (e) {
      throw Exception('Failed to get analysis statistics: $e');
    }
  }

  /// Get available security checks
  Future<List<Map<String, dynamic>>> getAvailableSecurityChecks() async {
    try {
      final uri = Uri.parse('$_baseUrl/checks');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return (data['available_checks'] as List).cast<Map<String, dynamic>>();
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } on SocketException {
      throw Exception('Unable to connect to API Analysis Service');
    } catch (e) {
      throw Exception('Failed to get available security checks: $e');
    }
  }

  /// Check if the service is healthy
  Future<bool> isServiceHealthy() async {
    try {
      final uri = Uri.parse('$_baseUrl/health');
      final response = await http.get(uri);
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
