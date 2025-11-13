import '../../domain/entities/api_analysis_entity.dart';

/// Data source for API analysis operations
abstract class ApiAnalysisDataSource {
  /// Analyze an API endpoint
  Future<Map<String, dynamic>> analyzeApiEndpoint(String endpoint);

  /// Get analysis history
  Future<List<Map<String, dynamic>>> getAnalysisHistory();

  /// Get specific analysis by ID
  Future<Map<String, dynamic>?> getAnalysisById(String id);
}
