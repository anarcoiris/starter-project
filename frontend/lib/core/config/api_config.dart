/// Base URL del API REST del prototipo (FastAPI). Sobrescribe con
/// `--dart-define=API_BASE_URL=http://10.0.2.2:8000` en emulador Android.
class ApiConfig {
  ApiConfig._();

  static const String backendBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    // Puerto host 9000 (api/docker-compose.yml); evita choque con otros servicios en :8000.
    defaultValue: 'http://127.0.0.1:9000',
  );
}
