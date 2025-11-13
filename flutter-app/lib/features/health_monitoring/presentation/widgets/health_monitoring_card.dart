import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/connection_status.dart';
import '../providers/health_monitoring_provider.dart';

class HealthMonitoringCard extends ConsumerStatefulWidget {
  const HealthMonitoringCard({super.key});

  @override
  ConsumerState<HealthMonitoringCard> createState() => _HealthMonitoringCardState();
}

class _HealthMonitoringCardState extends ConsumerState<HealthMonitoringCard> {
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    final status = ref.watch(connectivityStatusProvider);

    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const Text(
              'Health Monitoring Service Status',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildStatusDisplay(status),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _checkConnection,
              icon: _isLoading
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.refresh),
              label: Text(_isLoading ? 'Checking...' : 'Check Connection'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusDisplay(ConnectionStatus status) {
    return Column(
      children: [
        Icon(_getStatusIcon(status), size: 48, color: _getStatusColor(status)),
        const SizedBox(height: 8),
        Text(
          status.displayName,
          style: TextStyle(
            fontSize: 18,
            color: _getStatusColor(status),
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
    }
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

  void _checkConnection() async {
    setState(() {
      _isLoading = true;
    });

    // Update status to checking
    ref.read(connectivityStatusProvider.notifier).state = ConnectionStatus.checking;

    // Simulate connection check
    await Future.delayed(const Duration(seconds: 2));

    // For demo, assume connected
    setState(() {
      _isLoading = false;
      ref.read(connectivityStatusProvider.notifier).state = ConnectionStatus.connected;
    });
  }
}
