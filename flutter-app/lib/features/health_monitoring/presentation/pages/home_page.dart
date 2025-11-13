import 'package:flutter/material.dart';
import '../widgets/health_monitoring_card.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Security Orchestrator'),
        backgroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.white,
      ),
      body: const SingleChildScrollView(
        child: Column(
          children: [
            SizedBox(height: 24),
            Text(
              'Security Orchestrator Dashboard',
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.black87),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 8),
            Text(
              'Monitor and manage your security infrastructure',
              style: TextStyle(fontSize: 16, color: Colors.black54),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 32),
            HealthMonitoringCard(),
          ],
        ),
      ),
    );
  }
}
