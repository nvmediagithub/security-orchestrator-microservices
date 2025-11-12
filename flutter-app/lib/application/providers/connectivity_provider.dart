import 'package:riverpod/riverpod.dart';
import '../../domain/usecases/check_connectivity_usecase.dart';
import '../../domain/entities/connection_status.dart';
import '../../infrastructure/services/connectivity_service.dart';
import '../../infrastructure/api/connectivity_usecase_impl.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

// Infrastructure providers
final connectivityServiceProvider = Provider<ConnectivityService>((ref) {
  final connectivity = Connectivity();
  const backendUrl = 'http://localhost:8001'; // Health monitoring service URL
  return ConnectivityServiceImpl(connectivity, backendUrl);
});

// Use case providers
final checkConnectivityUseCaseProvider = Provider<CheckConnectivityUseCase>((ref) {
  final connectivityService = ref.watch(connectivityServiceProvider);
  return CheckConnectivityUseCaseImpl(connectivityService);
});

final getConnectivityStatusUseCaseProvider = Provider<GetConnectivityStatusUseCase>((ref) {
  final connectivityService = ref.watch(connectivityServiceProvider);
  return GetConnectivityStatusUseCaseImpl(connectivityService);
});

// State providers
final connectivityStatusProvider = StreamProvider<ConnectionStatus>((ref) {
  final useCase = ref.watch(getConnectivityStatusUseCaseProvider);
  return useCase.execute();
});

final connectivityNotifierProvider = StateNotifierProvider<ConnectivityNotifier, AsyncValue<ConnectionStatus>>((ref) {
  final useCase = ref.watch(checkConnectivityUseCaseProvider);
  return ConnectivityNotifier(useCase);
});

class ConnectivityNotifier extends StateNotifier<AsyncValue<ConnectionStatus>> {
  final CheckConnectivityUseCase _useCase;

  ConnectivityNotifier(this._useCase) : super(const AsyncValue.loading()) {
    checkConnectivity();
  }

  Future<void> checkConnectivity() async {
    state = const AsyncValue.loading();
    try {
      final status = await _useCase.execute();
      state = AsyncValue.data(status);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }
}