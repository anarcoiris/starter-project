import 'dart:developer' as developer;

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:get_it/get_it.dart';
import 'package:news_app_clean_architecture/core/config/api_config.dart';

/// En depuración, llama a [GET /health] del prototipo FastAPI y al endpoint de Ollama.
/// No bloquea el arranque si los servidores no están.
Future<void> probeBackendHealth(GetIt locator) async {
  if (!kDebugMode) return;
  
  // 1. Probe FastAPI Backend
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

  // 2. Probe Ollama
  try {
    final ollamaUrl = ApiConfig.ollamaBaseUrl;
    final dio = Dio(BaseOptions(connectTimeout: const Duration(seconds: 2)));
    final response = await dio.get(ollamaUrl);
    
    if (response.statusCode == 200) {
      developer.log(
        'Ollama Server OK at $ollamaUrl',
        name: 'SymmetryOllama',
      );
    }
  } catch (e) {
    developer.log(
      'Ollama Server no disponible en ${ApiConfig.ollamaBaseUrl}. Asegúrate de que Ollama esté corriendo.',
      name: 'SymmetryOllama',
    );
  }
}
