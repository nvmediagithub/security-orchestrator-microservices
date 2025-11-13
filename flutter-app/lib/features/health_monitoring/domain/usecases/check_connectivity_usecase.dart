import '../entities/connection_status.dart';

abstract class CheckConnectivityUseCase {
  Future<ConnectionStatus> execute();
}

abstract class GetConnectivityStatusUseCase {
  Stream<ConnectionStatus> execute();
}
