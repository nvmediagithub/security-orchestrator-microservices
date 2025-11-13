import '../entities/connection_status.dart';

abstract class HealthMonitoringRepository {
  Future<ConnectionStatus> checkConnectivity();
  Stream<ConnectionStatus> getConnectivityStatus();
}
