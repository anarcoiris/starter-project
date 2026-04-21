import 'dart:developer' as developer;

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:get_it/get_it.dart';

/// En depuración, llama a [GET /health] del prototipo FastAPI. No bloquea el arranque si el servidor no está.
Future<void> probeBackendHealth(GetIt locator) async {
  if (!kDebugMode) return;
  try {
    final dio = locator<Dio>(instanceName: 'backend');
    final response = await dio.get<Map<String, dynamic>>('/health');
    developer.log(
      'Symmetry API OK: ${response.data}',
      name: 'SymmetryAPI',
    );
  } catch (e, st) {
    developer.log(
      'Symmetry API no disponible (¿docker compose en api/?): $e',
      name: 'SymmetryAPI',
      error: e,
      stackTrace: st,
    );
  }
}
