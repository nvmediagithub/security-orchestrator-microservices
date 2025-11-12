import 'package:flutter/material.dart';
import 'package:riverpod/riverpod.dart';
import '../../domain/entities/connection_status.dart';
import '../../application/providers/connectivity_provider.dart';
import '../../domain/usecases/check_connectivity_usecase.dart';

class ConnectionStatusCard extends ConsumerWidget {
  const ConnectionStatusCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivityAsync = ref.watch(connectivityStatusProvider);

    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const Text(
              'Health Monitoring Service Status',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            connectivityAsync.when(
              data: (status) => _buildStatusDisplay(status),
              loading: () => _buildStatusDisplay(ConnectionStatus.checking),
              error: (error, stack) => _buildErrorDisplay(error),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                final notifier = ref.read(connectivityNotifierProvider.notifier);
                notifier.checkConnectivity();
              },
              icon: const Icon(Icons.refresh),
              label: const Text('Check Connection'),
            ),
          ],
        ),
      ),
    );
  }
}

  Widget _buildStatusDisplay(ConnectionStatus status) {
    final color = _getStatusColor(status);
    final icon = _getStatusIcon(status);

    return Column(
      children: [
        Icon(
          icon,
          size: 48,
          color: color,
        ),
        const SizedBox(height: 8),
        Text(
          status.displayName,
          style: TextStyle(
            fontSize: 18,
            color: color,
            fontWeight: FontWeight.w500,
          ),
        ),
        if (status == ConnectionStatus.checking)
          const Padding(
            padding: EdgeInsets.only(top: 8),
            child: SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
          ),
      ],
    );
  }

  Widget _buildErrorDisplay(Object error) {
    return Column(
      children: [
        const Icon(
          Icons.error_outline,
          size: 48,
          color: Colors.red,
        ),
        const SizedBox(height: 8),
        Text(
          'Connection Error',
          style: const TextStyle(
            fontSize: 18,
            color: Colors.red,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          error.toString(),
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontSize: 14,
            color: Colors.grey,
          ),
        ),
      ],
    );
  }

  Color _getStatusColor(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.connected:
        return Colors.green;
      case ConnectionStatus.disconnected:
        return Colors.orange;
      case ConnectionStatus.error:
        return Colors.red;
      case ConnectionStatus.checking:
        return Colors.blue;
    }
  }

  IconData _getStatusIcon(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.connected:
        return Icons.check_circle;
      case ConnectionStatus.disconnected:
        return Icons.wifi_off;
      case ConnectionStatus.error:
        return Icons.error;
      case ConnectionStatus.checking:
        return Icons.sync;
      default:
        return Icons.help;
    }
  }
}