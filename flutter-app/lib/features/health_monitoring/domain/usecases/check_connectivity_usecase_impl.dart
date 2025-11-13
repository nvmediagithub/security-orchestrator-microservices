import '../entities/connection_status.dart';
import '../repositories/health_monitoring_repository.dart';
import 'check_connectivity_usecase.dart';

class CheckConnectivityUseCaseImpl implements CheckConnectivityUseCase {
  final HealthMonitoringRepository _repository;

  CheckConnectivityUseCaseImpl(this._repository);

  @override
  Future<ConnectionStatus> execute() {
    return _repository.checkConnectivity();
  }
}

class GetConnectivityStatusUseCaseImpl implements GetConnectivityStatusUseCase {
  final HealthMonitoringRepository _repository;

  GetConnectivityStatusUseCaseImpl(this._repository);

  @override
  Stream<ConnectionStatus> execute() {
    return _repository.getConnectivityStatus();
  }
}
