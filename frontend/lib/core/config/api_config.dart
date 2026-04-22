/// Base URL del API REST del prototipo (FastAPI). Sobrescribe con
/// `--dart-define=API_BASE_URL=http://10.0.2.2:8000` en emulador Android.
class ApiConfig {
  ApiConfig._();

  static const String backendBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://uncovernews.ddns.net/api/v1',
  );

  static const String ollamaBaseUrl = String.fromEnvironment(
    'OLLAMA_BASE_URL',
    defaultValue: 'http://10.0.2.2:11434', // Android emulator localhost
  );
}
