import '../entities/api_analysis_entity.dart';

/// Use case for analyzing APIs
abstract class AnalyzeApiUseCase {
  /// Execute API analysis
  Future<ApiAnalysisEntity> execute(String endpoint);
}
