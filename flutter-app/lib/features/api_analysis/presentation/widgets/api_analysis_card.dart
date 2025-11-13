import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/api_analysis_entity.dart';
import '../providers/api_analysis_provider.dart';

/// Widget for displaying API analysis results
class ApiAnalysisCard extends ConsumerWidget {
  const ApiAnalysisCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final apiAnalysisState = ref.watch(apiAnalysisNotifierProvider);

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('API Analysis', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),

            // Input field for API endpoint
            _buildEndpointInput(ref),
            const SizedBox(height: 16),

            // Analysis results
            _buildAnalysisResults(apiAnalysisState, context),
          ],
        ),
      ),
    );
  }

  Widget _buildEndpointInput(WidgetRef ref) {
    final controller = TextEditingController();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Enter API Endpoint:', style: TextStyle(fontWeight: FontWeight.w500)),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                decoration: const InputDecoration(
                  hintText: 'https://api.example.com/v1/endpoint',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.link),
                ),
              ),
            ),
            const SizedBox(width: 8),
            ElevatedButton.icon(
              onPressed: () {
                final endpoint = controller.text.trim();
                if (endpoint.isNotEmpty) {
                  ref.read(apiAnalysisNotifierProvider.notifier).analyzeApi(endpoint);
                }
              },
              icon: const Icon(Icons.search),
              label: const Text('Analyze'),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildAnalysisResults(AsyncValue<ApiAnalysisEntity?> state, BuildContext context) {
    return state.when(
      data: (analysis) {
        if (analysis == null) {
          return const Center(
            child: Text(
              'Enter an API endpoint to analyze',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
          );
        }

        return _buildAnalysisContent(analysis, context);
      },
      loading: () => const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Analyzing API endpoint...'),
          ],
        ),
      ),
      error: (error, stackTrace) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error, color: Colors.red, size: 48),
            const SizedBox(height: 16),
            Text(
              'Analysis failed: $error',
              style: const TextStyle(color: Colors.red),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: () {
                // Could implement retry logic here
              },
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalysisContent(ApiAnalysisEntity analysis, BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Status and endpoint info
        Row(
          children: [
            Icon(
              analysis.analysis?.isSecure ?? false ? Icons.security : Icons.warning,
              color: analysis.analysis?.isSecure ?? false ? Colors.green : Colors.orange,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                analysis.endpoint,
                style: const TextStyle(fontWeight: FontWeight.w500),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Security status
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: (analysis.analysis?.isSecure ?? false)
                ? Colors.green.shade100
                : Colors.orange.shade100,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(
                analysis.analysis?.isSecure ?? false ? Icons.check_circle : Icons.warning,
                color: analysis.analysis?.isSecure ?? false ? Colors.green : Colors.orange,
              ),
              const SizedBox(width: 8),
              Text(
                analysis.analysis?.isSecure ?? false ? 'Secure API' : 'Potential Security Issues',
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: analysis.analysis?.isSecure ?? false
                      ? Colors.green.shade700
                      : Colors.orange.shade700,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Issues
        if (analysis.analysis?.issues.isNotEmpty ?? false) ...[
          _buildSectionTitle('Issues Found', Icons.bug_report, Colors.red),
          const SizedBox(height: 8),
          ...analysis.analysis!.issues.map((issue) => _buildIssueItem(issue)),
          const SizedBox(height: 16),
        ],

        // Recommendations
        if (analysis.analysis?.recommendations.isNotEmpty ?? false) ...[
          _buildSectionTitle('Recommendations', Icons.lightbulb, Colors.blue),
          const SizedBox(height: 8),
          ...analysis.analysis!.recommendations.map((rec) => _buildRecommendationItem(rec)),
          const SizedBox(height: 16),
        ],

        // Analysis details
        _buildSectionTitle('Analysis Details', Icons.info, Colors.grey),
        const SizedBox(height: 8),
        _buildDetailsList(analysis.analysis?.details ?? {}),

        // Timestamp
        const SizedBox(height: 16),
        Text(
          'Analyzed: ${analysis.timestamp.toLocal().toString().split(' ')[0]} '
          '${analysis.timestamp.toLocal().toString().split(' ')[1].split('.')[0]}',
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
      ],
    );
  }

  Widget _buildSectionTitle(String title, IconData icon, Color color) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 8),
        Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
      ],
    );
  }

  Widget _buildIssueItem(String issue) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.bug_report, color: Colors.red, size: 16),
          const SizedBox(width: 8),
          Expanded(child: Text(issue)),
        ],
      ),
    );
  }

  Widget _buildRecommendationItem(String recommendation) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.lightbulb, color: Colors.blue, size: 16),
          const SizedBox(width: 8),
          Expanded(child: Text(recommendation)),
        ],
      ),
    );
  }

  Widget _buildDetailsList(Map<String, dynamic> details) {
    return Column(
      children: details.entries.map((entry) {
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 2),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: 120,
                child: Text('${entry.key}:', style: const TextStyle(fontWeight: FontWeight.w500)),
              ),
              Expanded(child: Text(entry.value.toString())),
            ],
          ),
        );
      }).toList(),
    );
  }
}
