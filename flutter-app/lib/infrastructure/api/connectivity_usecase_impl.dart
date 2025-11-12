import '../../domain/usecases/check_connectivity_usecase.dart';
import '../../domain/entities/connection_status.dart';
import '../services/connectivity_service.dart';

class CheckConnectivityUseCaseImpl implements CheckConnectivityUseCase {
  final ConnectivityService _connectivityService;

  CheckConnectivityUseCaseImpl(this._connectivityService);

  @override
  Future<ConnectionStatus> execute() {
    return _connectivityService.checkBackendConnectivity();
  }
}

class GetConnectivityStatusUseCaseImpl implements GetConnectivityStatusUseCase {
  final ConnectivityService _connectivityService;

  GetConnectivityStatusUseCaseImpl(this._connectivityService);

  @override
  Stream<ConnectionStatus> execute() {
    return _connectivityService.connectivityStream;
  }
}