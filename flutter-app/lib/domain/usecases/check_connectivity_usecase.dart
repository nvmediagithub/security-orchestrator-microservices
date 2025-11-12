abstract class CheckConnectivityUseCase {
  Future<ConnectionStatus> execute();
}

abstract class GetConnectivityStatusUseCase {
  Stream<ConnectionStatus> execute();
}