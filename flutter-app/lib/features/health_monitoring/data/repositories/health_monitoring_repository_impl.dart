import '../../domain/entities/connection_status.dart';
import '../../domain/repositories/health_monitoring_repository.dart';
import '../datasources/health_monitoring_datasource.dart';

class HealthMonitoringRepositoryImpl implements HealthMonitoringRepository {
  final HealthMonitoringDatasource _datasource;

  HealthMonitoringRepositoryImpl(this._datasource);

  @override
  Future<ConnectionStatus> checkConnectivity() {
    return _datasource.checkBackendConnectivity();
  }

  @override
  Stream<ConnectionStatus> getConnectivityStatus() {
    return _datasource.connectivityStream;
  }
}
