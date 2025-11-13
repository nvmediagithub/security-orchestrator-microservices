import '../entities/api_analysis_entity.dart';

/// Repository interface for API analysis operations
abstract class ApiAnalysisRepository {
  /// Analyze an API endpoint
  Future<ApiAnalysisEntity> analyzeApi(String endpoint);

  /// Get analysis history
  Future<List<ApiAnalysisEntity>> getAnalysisHistory();

  /// Get specific analysis by ID
  Future<ApiAnalysisEntity?> getAnalysisById(String id);
}
