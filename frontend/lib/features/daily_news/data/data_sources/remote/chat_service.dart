import 'package:dio/dio.dart';
import 'package:news_app_clean_architecture/core/config/api_config.dart';

class ChatService {
  final Dio _dio;

  ChatService(this._dio);

  Future<String> getChatResponse(String prompt) async {
    try {
      final response = await _dio.post(
        '/ollama/api/generate',
        data: {
          'model': 'qwen:2.5b',
          'prompt': prompt,
          'stream': false,
        },
      );

      if (response.statusCode == 200) {
        return response.data['response'] ?? "No pude procesar la respuesta.";
      } else {
        return "Error del servidor: ${response.statusCode}";
      }
    } catch (e) {
      if (e is DioException) {
        return "Error de conexión: ${e.message}";
      }
      return "Error inesperado: $e";
    }
  }
}
