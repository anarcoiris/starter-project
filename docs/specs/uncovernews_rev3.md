# Plan de Revisión v2 — Symmetry News
**Versión:** 2.0  
**Fecha:** Abril 2026  
**Rama revisada:** `main` (fork actualizado)  
**Base:** REVIEW_PLAN v1.0

---

## Resumen de cambios respecto a v1

| Resultado | Cantidad |
|-----------|----------|
| ✅ Resueltos desde v1 | 5 |
| 🔄 Parcialmente resueltos | 3 |
| 🔴 Críticos que siguen abiertos | 4 |
| 🟠 Importantes que siguen abiertos | 7 |
| 🟡 Mejoras que siguen abiertas | 6 |
| 🆕 Nuevos problemas detectados | 7 |

---

## ✅ CERRADOS — Resueltos desde v1

### [C-05] Credenciales hardcodeadas — RESUELTO
`newsAPIKey` ahora usa `String.fromEnvironment('NEWS_API_KEY', defaultValue: '')`. La clave ya no está en texto plano en el código fuente.

**Acción pendiente:** Confirmar que la clave de NewsAPI en el proveedor fue rotada, dado que estuvo expuesta públicamente en la rama anterior.

---

### [B-03] `kDefaultImage` apuntaba a Google Search — RESUELTO
Ahora apunta a una imagen real de Unsplash con parámetros correctos de formato.

---

### [C-04] `PublishArticlePage` accedía directamente al repositorio — RESUELTO
Se creó `StorageRepository` como abstracción independiente y `StorageRepositoryImpl` como implementación. La página ahora usa `sl<StorageRepository>()`. Correcto.

---

### [I-05] TopicsPage con datos ficticios y sin funcionalidad — RESUELTO
Los tópicos ahora disparan `GetArticles(category: topic['id'])` en el bloc global y navegan de vuelta al feed. Los contadores hardcodeados fueron eliminados y reemplazados por "VER ALERTAS". Funcionalidad real implementada.

---

### [B-07] `print` de debug en producción (backend) — RESUELTO
El repositorio de artículos ahora usa `logger.debug(...)` correctamente. El sistema de logging estructurado está configurado en `main.py`.

---

## 🔄 PARCIALMENTE RESUELTOS — Requieren verificación adicional

### [B-04] Mismatch entre schema del backend y ArticleEntity — PARCIAL
`ArticleEntity` ahora incluye `tokensEarned: double?`. Es un avance, pero siguen sin mapearse `source`, `category`, `views`, `readTime`, `articleId` desde el backend al modelo Flutter. El mismatch persiste para todos esos campos.

**Estado:** 🔄  
**Acción:** Completar el mapeo o documentar explícitamente qué campos son out-of-scope para el cliente.

---

### [I-01] `fromJson` y `fromRawData` son aliases — PARCIAL
Ahora `fromRawData` delega a `fromJson` (antes era al revés), lo que es semánticamente más correcto. Pero siguen siendo dos métodos que hacen exactamente lo mismo, violando DRY.

**Estado:** 🔄  
**Acción:** Eliminar `fromRawData` y usar solo `fromJson`, o viceversa, en todos los call sites.

---

### [B-05] Generación de `articleId` frágil — PARCIAL
Se cambió el separador de `''` a `'_'` para URLs, lo que mejora la legibilidad. Pero el problema de colisiones sigue existiendo: `http://a.com/` → `http___a_com_` y `http://a.com` → `http___a_com` (son iguales sin trailing slash, colisión garantizada en la práctica).

**Estado:** 🔄  
**Acción:** Usar UUID v4 o hash SHA-256 de la URL. El paquete `uuid` ya está disponible en `pubspec.lock`.

---

## 🔴 BLOQUE 1 — Críticos que siguen abiertos

### [C-01] Duplicidad de configuración en el backend — SIGUE ABIERTO

**Archivos afectados:**
- `backend/fastapi/app/config.py`
- `backend/fastapi/app/core/config.py`

**Verificación:** ¿Ambos archivos siguen existiendo con clases `Settings` separadas? ¿`seed_mock_news.py` importa de `app/config.py` (sin `ollama_host`) mientras que `main.py` importa de `app/core/config.py`?

**Fix esperado:** Eliminar `app/config.py`. Consolidar toda la configuración en `app/core/config.py`. Actualizar el import en `seed_mock_news.py`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [C-02] Capa de presentación accede directamente a Firebase — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/features/auth/presentation/pages/profile_page.dart`

**Verificación:** ¿La página sigue importando `cloud_firestore` y usando `FirebaseFirestore.instance.collection('users').doc(user.uid).snapshots()` directamente?

**Fix esperado:** Exponer un stream de perfil de usuario a través del `AuthCubit` o un nuevo `ProfileCubit`. El dato de la bio debe llegar como estado del bloc, nunca como stream de Firestore en la vista.

**Violación:** Reglas 3.1.1 y 1.2.4 de `ARCHITECTURE_VIOLATIONS.md`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [C-03] ChatBloc accede directamente al Data Layer — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/features/daily_news/presentation/bloc/chat/chat_bloc.dart`

**Verificación:** ¿`ChatBloc` sigue recibiendo `ChatService` directamente? ¿Existen `ChatRepository` y `SendMessageUseCase`?

**Fix esperado:** Crear cadena completa: `ChatRepository` (interfaz domain) → `ChatRepositoryImpl` (implementa usando `ChatService`) → `SendMessageUseCase` → `ChatBloc` solo recibe el use case.

**Violación:** Regla 3.2.3 de `ARCHITECTURE_VIOLATIONS.md`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [C-06] JSON inválido en `.firebaserc` — SIGUE ABIERTO

**Archivos afectados:**
- `backend/firebase/.firebaserc`

**Verificación:** ¿El archivo sigue conteniendo un comentario JS (`// TODO: ADD PROJECT ID`) dentro del JSON, haciéndolo inválido?

**Fix esperado:** Reemplazar el comentario por el Project ID real o por el placeholder de string `"YOUR_PROJECT_ID"`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

## 🟠 BLOQUE 2 — Importantes que siguen abiertos

### [B-01] `ChatService` ignora el Dio inyectado — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/features/daily_news/data/data_sources/remote/chat_service.dart`

**Verificación:** ¿El método `_getOllamaResponse` crea su propio `Dio` interno con `BaseOptions` propias, ignorando el `_dio` del constructor?

**Fix esperado:** Registrar una instancia Dio dedicada para Ollama (`instanceName: 'ollama'`) en el `injection_container`. Usar esa instancia inyectada en `ChatService`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [B-02] `DioError` deprecado — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/core/resources/data_state.dart`

**Verificación:** ¿`DataState` usa `DioError?` en lugar de `DioException?`?

```bash
grep -r "DioError" frontend/lib
```

**Fix esperado:** Reemplazar `DioError` por `DioException` en `data_state.dart` y en todos los archivos que lo referencien. Con Dio 5.9.2 esto genera warnings que se convertirán en errores en versiones futuras.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [B-06] Búsqueda sin manejo de estados de carga/error — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/features/daily_news/presentation/pages/search/search_page.dart`

**Verificación:** ¿El callback `onChanged` devuelve silenciosamente 0 resultados si el estado del bloc no es `RemoteArticlesDone`?

**Fix esperado:** Manejar explícitamente `RemoteArticlesLoading` y `RemoteArticlesError` con mensajes descriptivos al usuario.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [B-08] Floor: PK nullable causa fallos silenciosos en DELETE — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/features/daily_news/data/models/article.dart`
- `frontend/lib/features/daily_news/data/data_sources/local/DAO/article_dao.dart`

**Verificación:** ¿`ArticleModel.id` sigue siendo `int?`? ¿Los artículos del backend (sin `id` numérico) se guardan con `id: null` y luego no pueden borrarse?

**Fix esperado:** Rediseñar la PK local usando `articleId` (String) como clave primaria en Floor, o generar un ID autoincremental desacoplado del ID de backend. Requiere migración de schema.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [B-09] WelcomePage: timer sin cancelación en dispose — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/features/auth/presentation/pages/welcome_page.dart`

**Verificación:** ¿El `Future.delayed` de 5s no está almacenado como `Timer` cancelable?

**Fix esperado:**
```dart
Timer? _navTimer;

@override
void initState() {
  super.initState();
  _navTimer = Timer(const Duration(seconds: 5), () {
    if (mounted) Navigator.pushReplacementNamed(context, '/DailyNews');
  });
}

@override
void dispose() {
  _navTimer?.cancel();
  _controller.dispose();
  super.dispose();
}
```

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [I-03] Analytics llamado directamente desde la página — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/features/daily_news/presentation/pages/home/daily_news.dart`

**Verificación:** ¿`_onArticlePressed` sigue llamando `sl<AnalyticsRepository>().trackArticleView(article)` directamente desde la UI?

**Fix esperado:** El tracking debe dispararse como efecto secundario en el bloc (evento `ArticleOpened` en `RemoteArticlesBloc`), nunca desde la página.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [I-04] Reglas de Firestore y Storage vacías — SIGUE ABIERTO

**Archivos afectados:**
- `backend/firebase/firestore.rules`
- `backend/firebase/storage.rules`

**Verificación:** ¿Ambos archivos tienen solo el esqueleto con comentarios TODO sin implementar?

**Fix esperado:** Implementar al menos las reglas mínimas:
- Lectura de artículos: solo usuarios autenticados.
- Escritura de artículos: solo el autor (`request.auth.uid == resource.data.authorId`).
- Storage: solo el propietario puede escribir en `users/{userId}/`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

## 🟡 BLOQUE 3 — Mejoras pendientes de v1

### [I-02] Parámetros fantasma en `NewsApiService` — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/features/daily_news/data/data_sources/remote/news_api_service.dart`

**Verificación:** ¿Los parámetros `apiKey` y `country` se reciben pero no se usan en el request HTTP? (Nota: `category` sí se usa ahora.)

**Fix esperado:** Eliminar `apiKey` y `country` de la firma o implementarlos como query params reales.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [I-06] `_buildScanlines()` construye 100 widgets estáticos — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/features/daily_news/presentation/pages/search/search_page.dart`

**Fix esperado:** Reemplazar con `CustomPainter` que dibuje las líneas directamente en canvas. Ver detalle en v1.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [I-07] `AuthCubit` como Factory con consumo implícito como Singleton — SIGUE ABIERTO

**Archivos afectados:**
- `frontend/lib/injection_container.dart`

**Verificación:** ¿`AuthCubit` sigue registrado con `registerFactory`?

**Fix esperado:** Cambiar a `registerLazySingleton` dado que el estado de autenticación es único en toda la sesión.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [I-08] Docker Compose sin health checks — SIGUE ABIERTO

**Archivos afectados:**
- `backend/fastapi/docker-compose.yml`

**Fix esperado:** Añadir health check a MongoDB y condicionar el inicio de `api` con `condition: service_healthy`. Ver detalle en v1.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

## 🆕 BLOQUE 4 — Nuevos problemas detectados en esta revisión

---

### [N-01] 🔴 Todos los usuarios comparten el mismo ID de recompensas

**Archivos afectados:**
- `frontend/lib/core/constants/constants.dart`
- `frontend/lib/features/daily_news/presentation/pages/article_detail/article_detail.dart`
- `frontend/lib/features/daily_news/presentation/pages/home/daily_news.dart`
- `frontend/lib/features/auth/presentation/pages/profile_page.dart`

**Problema:** La constante `kAlphaTesterId = 'sym_alpha_tester'` se usa como `userId` en todas las llamadas a la API de recompensas. Esto significa que todos los usuarios de la app comparten el mismo saldo y el mismo historial de transacciones. El sistema de rewards es completamente no funcional a nivel multiusuario.

```dart
// constants.dart
const String kAlphaTesterId = 'sym_alpha_tester'; // ← ID compartido por TODOS

// article_detail.dart
_rewardApiService.claimReward(kAlphaTesterId, ...); // ← mismo usuario para todos
```

**Fix esperado:** Obtener el `userId` real del `AuthCubit` en el momento de reclamar la recompensa. El `article_detail.dart` ya tiene acceso al `AuthCubit` desde el árbol de widgets. Eliminar `kAlphaTesterId`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [N-02] 🔴 Endpoints de debug expuestos sin autenticación en producción

**Archivos afectados:**
- `backend/fastapi/app/api/v1/endpoints/debug.py`
- `backend/fastapi/app/main.py`

**Problema:** El router `/api/v1/debug` está registrado en producción sin ningún middleware de autenticación. Los endpoints `GET /debug/db-stats` y `GET /debug/raw-article/{id}` exponen información interna de la base de datos (conteos de colecciones, documentos completos en formato BSON sin filtrar) a cualquier usuario de internet.

**Fix esperado:** Una de estas opciones:
- Desregistrar el router en producción usando una variable de entorno: `if settings.debug_mode: api_router.include_router(debug.router, ...)`.
- Proteger todos los endpoints de debug con un middleware de API key o auth básica.
- Moverlos a un servidor de administración separado no expuesto públicamente.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [N-03] 🔴 CORS configurado con `allow_origins=["*"]` en producción

**Archivos afectados:**
- `backend/fastapi/app/main.py`

**Problema:** El middleware CORS permite solicitudes desde cualquier origen. Combinado con los endpoints de debug sin auth, esto permite que cualquier sitio web externo haga peticiones a la API.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← cualquier origen puede llamar a la API
    allow_credentials=True,
    ...
)
```

Nota: `allow_credentials=True` combinado con `allow_origins=["*"]` es inválido según la spec y fastapi debería rechazarlo — en la práctica puede producir comportamiento inesperado según la versión.

**Fix esperado:** Restringir a los orígenes legítimos:
```python
allow_origins=["https://uncovernews.ddns.net", "http://localhost:*"]
```
O cargar la lista desde una variable de entorno `settings.allowed_origins`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [N-04] 🟠 `RewardCubit` viola la arquitectura — accede directamente al Data Source

**Archivos afectados:**
- `frontend/lib/features/daily_news/presentation/bloc/reward/reward_cubit.dart`

**Problema:** `RewardCubit` recibe `RewardApiService` (un data source) directamente, repitiendo exactamente el mismo error que `ChatBloc` (C-03). No existe `RewardRepository` ni `ClaimRewardUseCase`.

```dart
class RewardCubit extends Cubit<RewardState> {
  final RewardApiService _rewardApiService; // ← data source directo
```

**Fix esperado:** Crear la cadena completa: `RewardRepository` (interfaz) → `RewardRepositoryImpl` → `ClaimRewardUseCase` → `RewardCubit` solo recibe el use case.

**Violación:** Regla 3.2.3 de `ARCHITECTURE_VIOLATIONS.md`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [N-05] 🟠 `publish_article_page.dart` aún viola la arquitectura

**Archivos afectados:**
- `frontend/lib/features/daily_news/presentation/pages/publish_article/publish_article_page.dart`

**Problema:** Aunque la violación de `ArticleRepository` se corrigió (C-04), ahora la página usa `sl<StorageRepository>().uploadImage(...)` directamente. El repositorio de Storage es una capa de dominio, no un use case. La presentación no debe tocar repositorios directamente.

```dart
// publish_article_page.dart
imageUrl = await sl<StorageRepository>().uploadImage(_selectedImage!, authState.user.uid);
// ↑ acceso directo al repositorio desde la UI
```

**Fix esperado:** Crear `UploadImageUseCase` que envuelva `StorageRepository.uploadImage`. La página (o mejor, un `PublishArticleBloc` dedicado) llama al use case, nunca al repositorio.

**Violación:** Regla 3.2.3 de `ARCHITECTURE_VIOLATIONS.md`.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [N-06] 🟠 `android:usesCleartextTraffic="true"` activo en el manifiesto de producción

**Archivos afectados:**
- `frontend/android/app/src/main/AndroidManifest.xml`

**Problema:** El flag `android:usesCleartextTraffic="true"` está en el manifiesto principal (no en el de debug), lo que permite tráfico HTTP sin cifrar en la build de producción/release. Esto es una vulnerabilidad real si cualquier llamada HTTP escapa a la configuración de Caddy.

**Fix esperado:** Mover el flag solo al manifiesto de debug (`src/debug/AndroidManifest.xml`) y asegurar que todas las URLs de producción usen HTTPS. Para el emulador, usar network security config en lugar de el flag global.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

### [N-07] 🟠 Ingestión de noticias asigna `author_id` ficticio sin autenticación

**Archivos afectados:**
- `backend/fastapi/app/services/ingestion_service.py`

**Problema:** El servicio de ingestión crea artículos con `author="AI Journalist ({source_name})"` pero no incluye `author_id`. El schema de MongoDB (definido en `12_data_model.md`) requiere `author_id` como referencia a un usuario real. Los artículos ingestados no tienen autor válido, lo que:
- Impide que el sistema de reputación funcione sobre esos artículos.
- Podría romper queries que filtren por `author_id`.
- El modelo `ArticleCreate` en FastAPI tiene `author` como campo requerido pero no valida `author_id`, permitiendo documentos incompletos.

Además, el bloque `except` en `_refactor_with_ai` captura todas las excepciones silenciosamente:
```python
except:  # ← captura todo, incluyendo KeyboardInterrupt y SystemExit
    pass
```

**Fix esperado:** Crear un usuario sistema (`system_journalist`) en la colección `users` y asignar su ID a los artículos ingestados. Cambiar el `except` bare a `except Exception as e:` con logging apropiado.

**Estado:** ⬜  
**Asignado a:** ___  
**PR / Commit:** ___

---

## 📊 Resumen de progreso actualizado

| Bloque | Total | ✅ Resuelto | 🔄 Parcial | ⬜ Abierto |
|--------|-------|------------|-----------|-----------|
| 🔴 Críticos (v1) | 6 | 2 | 0 | 4 |
| 🟠 Importantes (v1) | 9 | 1 | 2 | 6 |
| 🟡 Mejoras (v1) | 8 | 2 | 1 | 5 |
| 🆕 Nuevos (v2) | 7 | 0 | 0 | 7 |
| **Total** | **30** | **5** | **3** | **22** |

---

## 📋 Orden de ataque recomendado (actualizado)

```
INMEDIATO (esta semana)
  └── N-01 (todos comparten el mismo userId) — afecta a TODOS los usuarios ya
  └── N-02 (endpoints debug sin auth en producción) — surface de ataque activa
  └── N-03 (CORS wildcard) — combinado con N-02, riesgo real

Semana siguiente — Arquitectura pendiente
  └── C-01 (config duplicada backend)
  └── C-02 (Firebase en presentación)
  └── C-03 (ChatBloc sin use case)
  └── N-04 (RewardCubit sin use case)
  └── N-05 (StorageRepository desde página)

Semana 3 — Bugs funcionales
  └── B-02 (DioError deprecado)
  └── B-06 (búsqueda sin estados)
  └── B-08 (Floor PK nullable)
  └── B-09 (Timer sin cancelación)
  └── N-06 (cleartext en producción)
  └── N-07 (ingestión sin author_id)

Semana 4 — Deuda técnica
  └── C-06 (firebaserc inválido)
  └── I-02, I-03, I-04, I-06, I-07, I-08
  └── Parciales: B-04, I-01, B-05
```

---

## 🏅 Reconocimiento de mejoras implementadas

Más allá de los bugs, esta revisión reconoce los avances positivos del ciclo anterior:

- **Sistema de recompensas end-to-end**: `RewardCubit`, `RewardApiService`, endpoint `/rewards/claim` con validación de tiempo mínimo y deduplicación por artículo. Conceptualmente sólido.
- **Logging estructurado en backend y frontend**: `SimpleBlocObserver`, interceptor de Dio, `developer.log` con nombres de canal. Mucho más trazable que antes.
- **Pipeline de ingestión de noticias con IA**: `IngestionService` con RSS feeds, refactorización con Ollama y caché de respuestas LLM en MongoDB. Overdelivery real.
- **Contratos blockchain**: `SymmetryToken.sol`, `RewardsVault.sol` y `SymmetryVesting.sol` con EIP-712, AccessControl y protección anti-replay. Diseño correcto para producción.
- **Filtrado por categoría funcional**: El feed ahora filtra por categoría desde `TopicsPage` usando el bloc global. Flujo correcto.
- **`StorageRepository` segregado**: Buena separación respecto a `ArticleRepository`, siguiendo SRP.
- **Script de generación de arquitectura** (`generate_structure.py`): Útil para onboarding y consistencia, bien documentado.

---

*Documento generado para el segundo ciclo de revisión técnica de Symmetry News — Abril 2026.*