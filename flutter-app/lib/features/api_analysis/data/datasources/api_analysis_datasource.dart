import '../../domain/entities/api_analysis_entity.dart';

/// Data source for API analysis operations
abstract class ApiAnalysisDataSource {
  /// Analyze a Swagger/OpenAPI specification
  Future<Map<String, dynamic>> analyzeSwaggerApi(String swaggerUrl);

  /// Analyze an API endpoint (legacy method)
  Future<Map<String, dynamic>> analyzeApiEndpoint(String endpoint);

  /// Get analysis history
  Future<List<Map<String, dynamic>>> getAnalysisHistory();

  /// Get specific analysis by ID
  Future<Map<String, dynamic>?> getAnalysisById(String id);
}
