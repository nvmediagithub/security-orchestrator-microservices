import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/usecases/check_connectivity_usecase.dart';
import '../../domain/usecases/check_connectivity_usecase_impl.dart';
import '../../data/repositories/health_monitoring_repository_impl.dart';
import '../../data/datasources/health_monitoring_datasource.dart';
import '../../domain/entities/connection_status.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

// Simple provider for connectivity status
final connectivityStatusProvider = StateProvider<ConnectionStatus>((ref) {
  return ConnectionStatus.checking;
});

// Provider for manual refresh
final connectivityRefreshProvider = StateProvider<bool>((ref) => false);
