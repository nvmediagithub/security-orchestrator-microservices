/// Domain entity representing Swagger API analysis results
class ApiAnalysisEntity {
  final String id;
  final String status;
  final String swaggerUrl;
  final DateTime timestamp;
  final AnalysisResult? analysis;
  final String? errorMessage;
  final ApiMetadata? metadata;
  final StructureAnalysis? structureAnalysis;
  final AiAnalysisResult? aiAnalysis;

  const ApiAnalysisEntity({
    required this.id,
    required this.status,
    required this.swaggerUrl,
    required this.timestamp,
    this.analysis,
    this.errorMessage,
    this.metadata,
    this.structureAnalysis,
    this.aiAnalysis,
  });

  factory ApiAnalysisEntity.fromJson(Map<String, dynamic> json) {
    return ApiAnalysisEntity(
      id: json['analysis_id'] as String? ?? json['id'] as String,
      status: json['success'] == true ? 'completed' : 'failed',
      swaggerUrl: json['source_url'] as String? ?? json['swaggerUrl'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      analysis: json['summary'] != null
          ? AnalysisResult.fromJson({
              'isSecure': (json['summary']['security_score'] as int) > 70,
              'issues': _extractIssues(json),
              'recommendations': _extractRecommendations(json),
              'details': json,
            })
          : null,
      errorMessage: json['error'] as String?,
      metadata: json['metadata'] != null
          ? ApiMetadata.fromJson(json['metadata'] as Map<String, dynamic>)
          : null,
      structureAnalysis: json['structure_analysis'] != null
          ? StructureAnalysis.fromJson(json['structure_analysis'] as Map<String, dynamic>)
          : null,
      aiAnalysis: json['ai_analysis'] != null
          ? AiAnalysisResult.fromJson(json['ai_analysis'] as Map<String, dynamic>)
          : null,
    );
  }

  static List<String> _extractIssues(Map<String, dynamic> json) {
    final issues = <String>[];

    // Extract issues from structure analysis
    if (json['structure_analysis'] != null) {
      final potentialIssues =
          json['structure_analysis']['potential_issues'] as Map<String, dynamic>?;
      if (potentialIssues != null) {
        potentialIssues.forEach((category, issueList) {
          for (var issue in issueList as List) {
            issues.add('$category: $issue');
          }
        });
      }
    }

    return issues;
  }

  static List<String> _extractRecommendations(Map<String, dynamic> json) {
    final recommendations = <String>[];

    if (json['recommendations'] != null) {
      for (var rec in json['recommendations'] as List) {
        recommendations.add(rec['description'] as String);
      }
    }

    return recommendations;
  }

  Map<String, dynamic> toJson() {
    return {
      'analysis_id': id,
      'success': status == 'completed',
      'source_url': swaggerUrl,
      'timestamp': timestamp.toIso8601String(),
      'summary': analysis?.toJson(),
      'error': errorMessage,
      'metadata': metadata?.toJson(),
      'structure_analysis': structureAnalysis?.toJson(),
      'ai_analysis': aiAnalysis?.toJson(),
    };
  }

  ApiAnalysisEntity copyWith({
    String? id,
    String? status,
    String? swaggerUrl,
    DateTime? timestamp,
    AnalysisResult? analysis,
    String? errorMessage,
    ApiMetadata? metadata,
    StructureAnalysis? structureAnalysis,
    AiAnalysisResult? aiAnalysis,
  }) {
    return ApiAnalysisEntity(
      id: id ?? this.id,
      status: status ?? this.status,
      swaggerUrl: swaggerUrl ?? this.swaggerUrl,
      timestamp: timestamp ?? this.timestamp,
      analysis: analysis ?? this.analysis,
      errorMessage: errorMessage ?? this.errorMessage,
      metadata: metadata ?? this.metadata,
      structureAnalysis: structureAnalysis ?? this.structureAnalysis,
      aiAnalysis: aiAnalysis ?? this.aiAnalysis,
    );
  }
}

class AnalysisResult {
  final bool isSecure;
  final List<String> issues;
  final List<String> recommendations;
  final Map<String, dynamic> details;
  final int securityScore;
  final int totalEndpoints;
  final int criticalIssues;
  final int highIssues;
  final int mediumIssues;
  final int lowIssues;
  final bool aiAnalysisAvailable;

  const AnalysisResult({
    required this.isSecure,
    required this.issues,
    required this.recommendations,
    required this.details,
    required this.securityScore,
    required this.totalEndpoints,
    this.criticalIssues = 0,
    this.highIssues = 0,
    this.mediumIssues = 0,
    this.lowIssues = 0,
    required this.aiAnalysisAvailable,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      isSecure: json['isSecure'] as bool,
      issues: (json['issues'] as List<dynamic>).cast<String>(),
      recommendations: (json['recommendations'] as List<dynamic>).cast<String>(),
      details: json['details'] as Map<String, dynamic>,
      securityScore: json['security_score'] as int? ?? 0,
      totalEndpoints: json['total_endpoints'] as int? ?? 0,
      criticalIssues: json['critical_issues'] as int? ?? 0,
      highIssues: json['high_issues'] as int? ?? 0,
      mediumIssues: json['medium_issues'] as int? ?? 0,
      lowIssues: json['low_issues'] as int? ?? 0,
      aiAnalysisAvailable: json['ai_analysis_available'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'isSecure': isSecure,
      'issues': issues,
      'recommendations': recommendations,
      'details': details,
      'security_score': securityScore,
      'total_endpoints': totalEndpoints,
      'critical_issues': criticalIssues,
      'high_issues': highIssues,
      'medium_issues': mediumIssues,
      'low_issues': lowIssues,
      'ai_analysis_available': aiAnalysisAvailable,
    };
  }
}

class ApiMetadata {
  final String title;
  final String version;
  final String? description;
  final String openapiVersion;
  final Map<String, dynamic> contact;
  final Map<String, dynamic> license;
  final String? termsOfService;

  const ApiMetadata({
    required this.title,
    required this.version,
    this.description,
    required this.openapiVersion,
    this.contact = const {},
    this.license = const {},
    this.termsOfService,
  });

  factory ApiMetadata.fromJson(Map<String, dynamic> json) {
    return ApiMetadata(
      title: json['title'] as String,
      version: json['version'] as String,
      description: json['description'] as String?,
      openapiVersion: json['openapi_version'] as String,
      contact: json['contact'] as Map<String, dynamic>? ?? {},
      license: json['license'] as Map<String, dynamic>? ?? {},
      termsOfService: json['terms_of_service'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'version': version,
      'description': description,
      'openapi_version': openapiVersion,
      'contact': contact,
      'license': license,
      'terms_of_service': termsOfService,
    };
  }
}

class StructureAnalysis {
  final EndpointsSummary summary;
  final SecurityAssessment securityAssessment;
  final ValidationResult validationCheck;
  final ApiStatistics statistics;

  const StructureAnalysis({
    required this.summary,
    required this.securityAssessment,
    required this.validationCheck,
    required this.statistics,
  });

  factory StructureAnalysis.fromJson(Map<String, dynamic> json) {
    return StructureAnalysis(
      summary: EndpointsSummary.fromJson(json['summary'] as Map<String, dynamic>),
      securityAssessment: SecurityAssessment.fromJson(
        json['security_assessment'] as Map<String, dynamic>,
      ),
      validationCheck: ValidationResult.fromJson(json['validation_check'] as Map<String, dynamic>),
      statistics: ApiStatistics.fromJson(json['statistics'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'summary': summary.toJson(),
      'security_assessment': securityAssessment.toJson(),
      'validation_check': validationCheck.toJson(),
      'statistics': statistics.toJson(),
    };
  }
}

class EndpointsSummary {
  final int totalCount;
  final Map<String, int> methods;
  final Map<String, List<String>> pathsByTag;
  final List<String> deprecatedEndpoints;
  final int securedEndpoints;
  final int unsecuredEndpoints;

  const EndpointsSummary({
    required this.totalCount,
    required this.methods,
    required this.pathsByTag,
    this.deprecatedEndpoints = const [],
    required this.securedEndpoints,
    required this.unsecuredEndpoints,
  });

  factory EndpointsSummary.fromJson(Map<String, dynamic> json) {
    return EndpointsSummary(
      totalCount: json['total_count'] as int,
      methods: Map<String, int>.from(json['methods'] as Map),
      pathsByTag: Map<String, List<String>>.from(
        json['paths_by_tag'].map(
          (key, value) => MapEntry(key as String, List<String>.from(value as List)),
        ),
      ),
      deprecatedEndpoints: (json['deprecated_endpoints'] as List<dynamic>).cast<String>(),
      securedEndpoints: json['secured_endpoints'] as int,
      unsecuredEndpoints: json['unsecured_endpoints'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_count': totalCount,
      'methods': methods,
      'paths_by_tag': pathsByTag,
      'deprecated_endpoints': deprecatedEndpoints,
      'secured_endpoints': securedEndpoints,
      'unsecured_endpoints': unsecuredEndpoints,
    };
  }
}

class SecurityAssessment {
  final bool hasAuthentication;
  final bool globalSecurityDefined;
  final List<String> unprotectedEndpoints;
  final List<String> protectedEndpoints;
  final List<String> securityRecommendations;

  const SecurityAssessment({
    required this.hasAuthentication,
    required this.globalSecurityDefined,
    this.unprotectedEndpoints = const [],
    this.protectedEndpoints = const [],
    this.securityRecommendations = const [],
  });

  factory SecurityAssessment.fromJson(Map<String, dynamic> json) {
    return SecurityAssessment(
      hasAuthentication: json['has_authentication'] as bool,
      globalSecurityDefined: json['global_security_defined'] as bool,
      unprotectedEndpoints: (json['unprotected_endpoints'] as List<dynamic>).cast<String>(),
      protectedEndpoints: (json['protected_endpoints'] as List<dynamic>).cast<String>(),
      securityRecommendations: (json['security_recommendations'] as List<dynamic>).cast<String>(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'has_authentication': hasAuthentication,
      'global_security_defined': globalSecurityDefined,
      'unprotected_endpoints': unprotectedEndpoints,
      'protected_endpoints': protectedEndpoints,
      'security_recommendations': securityRecommendations,
    };
  }
}

class ValidationResult {
  final bool isValid;
  final List<String> errors;
  final List<String> warnings;
  final List<String> info;

  const ValidationResult({
    required this.isValid,
    this.errors = const [],
    this.warnings = const [],
    this.info = const [],
  });

  factory ValidationResult.fromJson(Map<String, dynamic> json) {
    return ValidationResult(
      isValid: json['is_valid'] as bool,
      errors: (json['errors'] as List<dynamic>).cast<String>(),
      warnings: (json['warnings'] as List<dynamic>).cast<String>(),
      info: (json['info'] as List<dynamic>).cast<String>(),
    );
  }

  Map<String, dynamic> toJson() {
    return {'is_valid': isValid, 'errors': errors, 'warnings': warnings, 'info': info};
  }
}

class ApiStatistics {
  final int totalEndpoints;
  final int pathsCount;
  final int getEndpoints;
  final int postEndpoints;
  final int putEndpoints;
  final int deleteEndpoints;
  final int patchEndpoints;
  final int schemasCount;

  const ApiStatistics({
    required this.totalEndpoints,
    required this.pathsCount,
    required this.getEndpoints,
    required this.postEndpoints,
    required this.putEndpoints,
    required this.deleteEndpoints,
    required this.patchEndpoints,
    required this.schemasCount,
  });

  factory ApiStatistics.fromJson(Map<String, dynamic> json) {
    return ApiStatistics(
      totalEndpoints: json['total_endpoints'] as int,
      pathsCount: json['paths_count'] as int,
      getEndpoints: json['get_endpoints'] as int,
      postEndpoints: json['post_endpoints'] as int,
      putEndpoints: json['put_endpoints'] as int,
      deleteEndpoints: json['delete_endpoints'] as int,
      patchEndpoints: json['patch_endpoints'] as int,
      schemasCount: json['schemas_count'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_endpoints': totalEndpoints,
      'paths_count': pathsCount,
      'get_endpoints': getEndpoints,
      'post_endpoints': postEndpoints,
      'put_endpoints': putEndpoints,
      'delete_endpoints': deleteEndpoints,
      'patch_endpoints': patchEndpoints,
      'schemas_count': schemasCount,
    };
  }
}

class AiAnalysisResult {
  final bool success;
  final String? analysis;
  final String? model;
  final int? tokensUsed;
  final String? error;

  const AiAnalysisResult({
    required this.success,
    this.analysis,
    this.model,
    this.tokensUsed,
    this.error,
  });

  factory AiAnalysisResult.fromJson(Map<String, dynamic> json) {
    return AiAnalysisResult(
      success: json['success'] as bool,
      analysis: json['analysis'] as String?,
      model: json['model'] as String?,
      tokensUsed: json['tokens_used'] as int?,
      error: json['error'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'analysis': analysis,
      'model': model,
      'tokens_used': tokensUsed,
      'error': error,
    };
  }
}
