import 'dart:developer' as developer;
import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:news_app_clean_architecture/core/config/api_config.dart';

class ChatService {
  final Dio _dio;

  ChatService(this._dio);

  Future<String> getChatResponse(String prompt) async {
    try {
      // Intento 1: Servidor Local (Ollama Container)
      final localDio = Dio(BaseOptions(
        baseUrl: ApiConfig.ollamaBaseUrl,
        connectTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 15),
      ));

      developer.log('Intentando petición a Ollama (${ApiConfig.ollamaBaseUrl}) con modelo qwen2.5:3b', name: 'SymmetryChat');

      final response = await localDio.post(
        '/api/generate',
        data: {
          'model': 'qwen2.5:3b',
          'prompt': prompt,
          'stream': false,
        },
      );

      if (response.statusCode == 200) {
        developer.log('Respuesta recibida de Ollama', name: 'SymmetryChat');
        return response.data['response'] ?? "No pude procesar la respuesta.";
      } else {
        developer.log('Ollama devolvió status ${response.statusCode}, pasando a OpenAI', name: 'SymmetryChat');
        return await _getOpenAIResponse(prompt);
      }
    } catch (e) {
      developer.log('Ollama no disponible o error: $e, pasando a OpenAI', name: 'SymmetryChat');
      // Fallback a OpenAI (gpt-4o-mini) si el contenedor Ollama no responde
      return await _getOpenAIResponse(prompt);
    }
  }

  Future<String> _getOpenAIResponse(String prompt) async {
    try {
      final apiKey = dotenv.env['OPENAI_API_KEY'];
      if (apiKey == null || apiKey.isEmpty) {
        developer.log('OPENAI_API_KEY no encontrada en .env', name: 'SymmetryChat');
        return "Servidor local offline y no hay API Key de respaldo.";
      }

      final openAiDio = Dio(BaseOptions(
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 20),
      ));
      
      final response = await openAiDio.post(
        'https://api.openai.com/v1/chat/completions',
        options: Options(
          headers: {
            'Authorization': 'Bearer $apiKey',
            'Content-Type': 'application/json',
          },
        ),
        data: {
          'model': 'gpt-4o-mini',
          'messages': [
            {'role': 'system', 'content': 'Eres el Owl Assistant de Symmetry. Responde de forma técnica y elegante.'},
            {'role': 'user', 'content': prompt}
          ],
        },
      );

      if (response.statusCode == 200) {
        return response.data['choices'][0]['message']['content'];
      }
      return "Error de respaldo (AI): ${response.statusCode}";
    } on DioException catch (e) {
      developer.log('Error de OpenAI: ${e.type} - ${e.message}', name: 'SymmetryChat', error: e);
      if (e.response?.statusCode == 401) {
        return "Error de autenticación: La API Key de OpenAI es inválida.";
      }
      return "Sistemas fuera de línea. Por favor, comprueba tu conexión.";
    } catch (e) {
      developer.log('Error inesperado en ChatService: $e', name: 'SymmetryChat', error: e);
      return "Sistemas fuera de línea. Por favor, comprueba tu conexión.";
    }
  }
}
