/// Domain entity representing API analysis results
class ApiAnalysisEntity {
  final String id;
  final String status;
  final String endpoint;
  final DateTime timestamp;
  final AnalysisResult? analysis;
  final String? errorMessage;

  const ApiAnalysisEntity({
    required this.id,
    required this.status,
    required this.endpoint,
    required this.timestamp,
    this.analysis,
    this.errorMessage,
  });

  factory ApiAnalysisEntity.fromJson(Map<String, dynamic> json) {
    return ApiAnalysisEntity(
      id: json['id'] as String,
      status: json['status'] as String,
      endpoint: json['endpoint'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      analysis: json['analysis'] != null
          ? AnalysisResult.fromJson(json['analysis'] as Map<String, dynamic>)
          : null,
      errorMessage: json['errorMessage'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'status': status,
      'endpoint': endpoint,
      'timestamp': timestamp.toIso8601String(),
      'analysis': analysis?.toJson(),
      'errorMessage': errorMessage,
    };
  }

  ApiAnalysisEntity copyWith({
    String? id,
    String? status,
    String? endpoint,
    DateTime? timestamp,
    AnalysisResult? analysis,
    String? errorMessage,
  }) {
    return ApiAnalysisEntity(
      id: id ?? this.id,
      status: status ?? this.status,
      endpoint: endpoint ?? this.endpoint,
      timestamp: timestamp ?? this.timestamp,
      analysis: analysis ?? this.analysis,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class AnalysisResult {
  final bool isSecure;
  final List<String> issues;
  final List<String> recommendations;
  final Map<String, dynamic> details;

  const AnalysisResult({
    required this.isSecure,
    required this.issues,
    required this.recommendations,
    required this.details,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      isSecure: json['isSecure'] as bool,
      issues: (json['issues'] as List<dynamic>).cast<String>(),
      recommendations: (json['recommendations'] as List<dynamic>).cast<String>(),
      details: json['details'] as Map<String, dynamic>,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'isSecure': isSecure,
      'issues': issues,
      'recommendations': recommendations,
      'details': details,
    };
  }
}
