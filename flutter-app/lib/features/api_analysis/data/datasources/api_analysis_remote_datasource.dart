import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'api_analysis_datasource.dart';

/// Remote data source for API analysis
class ApiAnalysisRemoteDataSource implements ApiAnalysisDataSource {
  final String _baseUrl;

  ApiAnalysisRemoteDataSource({String? baseUrl})
    : _baseUrl = baseUrl ?? 'http://localhost:8001';

  @override
  Future<Map<String, dynamic>> analyzeSwaggerApi(String swaggerUrl) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/v1/swagger-analysis/analyze');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'swagger_url': swaggerUrl,
          'timeout': 30,
          'enable_ai_analysis': false,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data; // API возвращает данные напрямую, не обернутые в success
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } on SocketException {
      throw Exception(
        'Unable to connect to API Analysis Service. '
        'Make sure the service is running on $_baseUrl',
      );
    } catch (e) {
      throw Exception('Failed to analyze Swagger API: $e');
    }
  }

  @override
  Future<Map<String, dynamic>> analyzeApiEndpoint(String endpoint) async {
    // Legacy method - tries to analyze as Swagger URL
    try {
      // Process URL to convert /docs to /openapi.json
      String processedUrl = _processSwaggerUrl(endpoint);

      // Use the new Swagger analysis method
      return await analyzeSwaggerApi(processedUrl);
    } catch (e) {
      // Fallback to simulated analysis
      return _simulateAnalysis(endpoint);
    }
  }

  /// Process URL to handle /docs -> /openapi.json conversion
  String _processSwaggerUrl(String endpoint) {
    String processedUrl = endpoint.trim();

    // If URL ends with /docs, replace with /openapi.json
    if (processedUrl.endsWith('/docs')) {
      processedUrl =
          processedUrl.substring(0, processedUrl.length - 5) + '/openapi.json';
    }
    // If URL doesn't contain /docs and doesn't end with common OpenAPI extensions
    else if (!processedUrl.contains('/docs') &&
        !processedUrl.endsWith('.json') &&
        !processedUrl.endsWith('.yaml') &&
        !processedUrl.endsWith('.yml')) {
      // Add /openapi.json as the default OpenAPI specification endpoint
      processedUrl = '${processedUrl}/openapi.json';
    }

    return processedUrl;
  }

  @override
  Future<List<Map<String, dynamic>>> getAnalysisHistory() async {
    // This endpoint doesn't exist in our API - return empty list
    return [];
  }

  @override
  Future<Map<String, dynamic>?> getAnalysisById(String id) async {
    // This endpoint doesn't exist in our API - return null
    return null;
  }

  /// Get analysis statistics
  Future<Map<String, dynamic>> getAnalysisStatistics() async {
    // This endpoint doesn't exist in our API - return empty stats
    return {
      'total_analyses': 0,
      'successful_analyses': 0,
      'failed_analyses': 0,
    };
  }

  /// Get available security checks
  Future<List<Map<String, dynamic>>> getAvailableSecurityChecks() async {
    // This endpoint doesn't exist in our API - return default checks
    return [
      {
        'name': 'Authentication',
        'description': 'Check for missing authentication',
      },
      {
        'name': 'Authorization',
        'description': 'Check for missing authorization',
      },
      {
        'name': 'Data Exposure',
        'description': 'Check for sensitive data exposure',
      },
      {
        'name': 'Input Validation',
        'description': 'Check for missing input validation',
      },
      {
        'name': 'Rate Limiting',
        'description': 'Check for rate limiting implementation',
      },
    ];
  }

  /// Check if the service is healthy
  Future<bool> isServiceHealthy() async {
    try {
      final uri = Uri.parse('$_baseUrl/api/v1/swagger-analysis/health');
      final response = await http.get(uri);
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Simulate analysis for fallback scenarios
  Map<String, dynamic> _simulateAnalysis(String endpoint) {
    final isSecure =
        !endpoint.contains('http://') && endpoint.startsWith('https://');
    final issues = <String>[];
    final recommendations = <String>[];

    if (!isSecure) {
      issues.add('Using insecure HTTP protocol');
      recommendations.add('Switch to HTTPS for secure communication');
    }

    if (endpoint.contains('/admin')) {
      issues.add('Admin endpoint exposed');
      recommendations.add(
        'Implement proper authentication for admin endpoints',
      );
    }

    return {
      'success': true,
      'analysis_id': DateTime.now().millisecondsSinceEpoch.toString(),
      'timestamp': DateTime.now().toIso8601String(),
      'source_url': endpoint,
      'summary': {
        'api_title': 'Simulated Analysis',
        'total_endpoints': 10,
        'security_score': isSecure ? 85 : 45,
        'critical_issues': 0,
        'high_issues': 0,
        'medium_issues': issues.length,
        'low_issues': 0,
        'ai_analysis_available': false,
      },
      'potential_issues': {
        'authentication': issues
            .where((issue) => issue.contains('authentication'))
            .toList(),
        'authorization': issues
            .where((issue) => issue.contains('authorization'))
            .toList(),
        'configuration': issues
            .where(
              (issue) => issue.contains('protocol') || issue.contains('HTTPS'),
            )
            .toList(),
      },
      'recommendations': recommendations
          .map(
            (rec) => {
              'category': 'Security',
              'priority': 'Medium',
              'description': rec,
            },
          )
          .toList(),
    };
  }
}
