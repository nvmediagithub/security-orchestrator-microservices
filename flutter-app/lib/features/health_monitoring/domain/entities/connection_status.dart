enum ConnectionStatus { connected, disconnected, error, checking }

extension ConnectionStatusExtension on ConnectionStatus {
  String get displayName {
    switch (this) {
      case ConnectionStatus.connected:
        return 'Connected';
      case ConnectionStatus.disconnected:
        return 'Disconnected';
      case ConnectionStatus.error:
        return 'Connection Error';
      case ConnectionStatus.checking:
        return 'Checking...';
    }
  }

  bool get isOnline => this == ConnectionStatus.connected;
}
