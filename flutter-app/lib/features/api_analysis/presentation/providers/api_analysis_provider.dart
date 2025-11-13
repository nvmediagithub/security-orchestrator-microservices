import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/api_analysis_entity.dart';
import '../../domain/repositories/api_analysis_repository.dart';
import '../../data/repositories/api_analysis_repository_impl.dart';
import '../../data/datasources/api_analysis_remote_datasource.dart';

/// Implementation of AnalyzeApiUseCase
class AnalyzeApiUseCase {
  final ApiAnalysisRepository _repository;

  const AnalyzeApiUseCase(this._repository);

  Future<ApiAnalysisEntity> execute(String endpoint) {
    return _repository.analyzeApi(endpoint);
  }
}

/// Provider for API analysis operations
class ApiAnalysisNotifier extends StateNotifier<AsyncValue<ApiAnalysisEntity?>> {
  final AnalyzeApiUseCase _analyzeApiUseCase;

  ApiAnalysisNotifier(this._analyzeApiUseCase) : super(const AsyncValue.data(null));

  /// Analyze an API endpoint
  Future<void> analyzeApi(String endpoint) async {
    state = const AsyncValue.loading();

    try {
      final result = await _analyzeApiUseCase.execute(endpoint);
      state = AsyncValue.data(result);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  /// Clear current analysis
  void clearAnalysis() {
    state = const AsyncValue.data(null);
  }
}

/// Providers
final analyzeApiUseCaseProvider = Provider<AnalyzeApiUseCase>((ref) {
  // Create the repository with remote data source
  final repository = ApiAnalysisRepositoryImpl(ApiAnalysisRemoteDataSource());
  return AnalyzeApiUseCase(repository);
});

final apiAnalysisNotifierProvider =
    StateNotifierProvider<ApiAnalysisNotifier, AsyncValue<ApiAnalysisEntity?>>((ref) {
      final useCase = ref.read(analyzeApiUseCaseProvider);
      return ApiAnalysisNotifier(useCase);
    });
