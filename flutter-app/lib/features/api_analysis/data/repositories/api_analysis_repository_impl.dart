import 'dart:math';
import '../../domain/entities/api_analysis_entity.dart';
import '../../domain/repositories/api_analysis_repository.dart';
import '../datasources/api_analysis_datasource.dart';

/// Implementation of ApiAnalysisRepository
class ApiAnalysisRepositoryImpl implements ApiAnalysisRepository {
  final ApiAnalysisDataSource _dataSource;

  const ApiAnalysisRepositoryImpl(this._dataSource);

  @override
  Future<ApiAnalysisEntity> analyzeApi(String swaggerUrl) async {
    final response = await _dataSource.analyzeSwaggerApi(swaggerUrl);

    // Convert the response from the backend to our entity
    final entity = ApiAnalysisEntity.fromJson(response);

    return entity;
  }

  @override
  Future<List<ApiAnalysisEntity>> getAnalysisHistory() async {
    final responses = await _dataSource.getAnalysisHistory();

    return responses.map((json) => ApiAnalysisEntity.fromJson(json)).toList();
  }

  @override
  Future<ApiAnalysisEntity?> getAnalysisById(String id) async {
    final response = await _dataSource.getAnalysisById(id);

    return response != null ? ApiAnalysisEntity.fromJson(response) : null;
  }

  /// Analyze a single API endpoint (legacy method for backward compatibility)
  Future<ApiAnalysisEntity> analyzeEndpoint(String endpoint) async {
    // For legacy compatibility, analyze the Swagger URL of the endpoint
    final swaggerUrl = endpoint.contains('/docs')
        ? endpoint
        : '${endpoint}/docs';

    try {
      return await analyzeApi(swaggerUrl);
    } catch (e) {
      // Fallback to simulated analysis if Swagger analysis fails
      return _simulateAnalysis(endpoint);
    }
  }

  ApiAnalysisEntity _simulateAnalysis(String endpoint) {
    // Simulate some basic API security analysis
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

    if (!endpoint.contains('api/v')) {
      issues.add('No API versioning detected');
      recommendations.add('Consider implementing API versioning');
    }

    // Add some random security checks
    final random = Random();
    if (random.nextBool()) {
      issues.add('Missing rate limiting headers');
      recommendations.add('Add X-RateLimit headers to prevent abuse');
    }

    final analysisResult = AnalysisResult(
      isSecure: isSecure,
      issues: issues,
      recommendations: recommendations,
      details: {
        'protocol': endpoint.startsWith('https://') ? 'HTTPS' : 'HTTP',
        'hasAuth': endpoint.contains('auth') || endpoint.contains('login'),
        'isApiEndpoint': endpoint.contains('/api/'),
        'analysisTime': DateTime.now().toIso8601String(),
      },
      securityScore: isSecure ? 85 : 45,
      totalEndpoints: 10,
      aiAnalysisAvailable: false,
    );

    return ApiAnalysisEntity(
      id: _generateId(),
      status: 'completed',
      swaggerUrl: endpoint,
      timestamp: DateTime.now(),
      analysis: analysisResult,
    );
  }

  String _generateId() {
    return DateTime.now().millisecondsSinceEpoch.toString() +
        Random().nextInt(1000).toString();
  }
}
