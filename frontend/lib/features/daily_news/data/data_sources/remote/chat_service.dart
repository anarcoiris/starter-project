import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:news_app_clean_architecture/core/config/api_config.dart';

class ChatService {
  final Dio _dio;

  ChatService(this._dio);

  Future<String> getChatResponse(String prompt) async {
    try {
      // Intento 1: Servidor Local (Ollama)
      final response = await _dio.post(
        '/ollama/api/generate',
        data: {
          'model': 'qwen:2.5b',
          'prompt': prompt,
          'stream': false,
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return response.data['response'] ?? "No pude procesar la respuesta.";
      } else {
        return await _getOpenAIResponse(prompt);
      }
    } catch (e) {
      // Fallback a OpenAI si el servidor local falla
      return await _getOpenAIResponse(prompt);
    }
  }

  Future<String> _getOpenAIResponse(String prompt) async {
    try {
      final apiKey = dotenv.env['OPENAI_API_KEY'];
      if (apiKey == null || apiKey.isEmpty) {
        return "Servidor local offline y no hay API Key de respaldo.";
      }

      final openAiDio = Dio();
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
    } catch (e) {
      return "Sistemas fuera de línea. Por favor, comprueba tu conexión.";
    }
  }
}
