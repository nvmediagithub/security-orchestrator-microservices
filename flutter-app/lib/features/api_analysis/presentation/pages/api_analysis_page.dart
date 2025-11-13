import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/api_analysis_card.dart';
import '../providers/api_analysis_provider.dart';

/// Page for API Analysis functionality
class ApiAnalysisPage extends ConsumerWidget {
  const ApiAnalysisPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('API Security Analysis'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              // Clear current analysis
              ref.read(apiAnalysisNotifierProvider.notifier).clearAnalysis();
            },
            tooltip: 'Clear Analysis',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Introduction card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.shield_outlined, size: 32, color: Colors.blue),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'API Security Analyzer',
                                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Analyze API endpoints for security vulnerabilities and best practices',
                                style: TextStyle(color: Colors.grey, fontSize: 14),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    // Features list
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildFeatureItem(
                          Icons.check_circle,
                          'Protocol Security Check',
                          'Verify HTTPS usage and identify insecure HTTP endpoints',
                        ),
                        const SizedBox(height: 8),
                        _buildFeatureItem(
                          Icons.warning,
                          'Security Vulnerability Detection',
                          'Identify common security issues like exposed admin endpoints',
                        ),
                        const SizedBox(height: 8),
                        _buildFeatureItem(
                          Icons.lightbulb,
                          'Best Practice Recommendations',
                          'Get actionable recommendations to improve API security',
                        ),
                        const SizedBox(height: 8),
                        _buildFeatureItem(
                          Icons.analytics,
                          'Detailed Analysis Reports',
                          'Comprehensive analysis with technical details and metrics',
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Main analysis card
            ApiAnalysisCard(),

            const SizedBox(height: 24),

            // Additional information
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Analysis Features',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 12),
                    Text('• Protocol analysis (HTTP/HTTPS)', style: TextStyle(fontSize: 14)),
                    Text('• Authentication endpoint detection', style: TextStyle(fontSize: 14)),
                    Text('• API versioning verification', style: TextStyle(fontSize: 14)),
                    Text('• Admin endpoint exposure check', style: TextStyle(fontSize: 14)),
                    Text('• Security headers analysis', style: TextStyle(fontSize: 14)),
                    Text('• Rate limiting recommendations', style: TextStyle(fontSize: 14)),
                    const SizedBox(height: 16),
                    Text(
                      'Note: This is a demo implementation with mock analysis. '
                      'A real implementation would integrate with security scanning services.',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureItem(IconData icon, String title, String description) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: Colors.blue),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
              const SizedBox(height: 2),
              Text(description, style: const TextStyle(fontSize: 12, color: Colors.grey)),
            ],
          ),
        ),
      ],
    );
  }
}
