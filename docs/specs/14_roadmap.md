# 14_ROADMAP.md

## 1. Purpose

Este documento define el orden de implementación recomendado,
agrupado por fases, con criterios claros de "done" para cada una.

---

## 2. Filosofía

> "Entregar una base sólida, limpia y ampliable."

El orden siempre es:
1. Schema de datos
2. Backend (Data + Domain layers)
3. Frontend funcional
4. Lógica de negocio
5. Documentación
6. Capas avanzadas

Nunca se construye la capa N+1 sin que la capa N esté estable.

---

## 3. Fase 0 — Setup (Día 1)

**Objetivo:** Entorno de desarrollo funcionando end-to-end.

### Backend
- [ ] `docker-compose.yml` con MongoDB + FastAPI + Caddy arriba
- [ ] Conexión Motor → MongoDB verificada
- [ ] `GET /health` devuelve 200

### Frontend
- [ ] Proyecto Flutter creado con Clean Architecture
- [ ] `dio` configurado apuntando al backend local
- [ ] `flutter run` compila y muestra pantalla vacía

**Done cuando:** el frontend puede hacer una request al backend y recibir respuesta.

---

## 4. Fase 1 — MVP Core (Días 2–5)

**Objetivo:** La funcionalidad principal del assignment funcionando.

### Backend
- [ ] Schema MongoDB definido e índices creados
- [ ] CRUD completo de artículos (`GET /articles`, `POST /articles`, etc.)
- [ ] Autenticación JWT básica (`/auth/register`, `/auth/login`)
- [ ] Endpoint de subida de imagen (`/upload/thumbnail`)
- [ ] Validaciones de entrada con Pydantic
- [ ] Caddyfile funcionando como reverse proxy

### Flutter — Domain Layer
- [ ] Entidades: `Article`, `User`
- [ ] Interfaces de repositorio: `ArticleRepository`, `UserRepository`
- [ ] Use Cases con mock data: `GetArticles`, `GetArticleById`, `CreateArticle`

### Flutter — Presentation Layer
- [ ] `AuthCubit`: login, registro, sesión
- [ ] `FeedCubit`: lista de artículos paginada
- [ ] `ArticleDetailCubit`: carga de artículo
- [ ] `CreateArticleCubit`: formulario y validación

### Flutter — UI
- [ ] `FeedScreen`: lista de artículos
- [ ] `ArticleDetailScreen`: contenido completo
- [ ] `CreateArticleScreen`: formulario de creación
- [ ] `LoginScreen` / `RegisterScreen`

### Flutter — Data Layer
- [ ] `ArticleRepositoryImpl` usando `dio`
- [ ] `UserRepositoryImpl` usando `dio`
- [ ] Subida de imagen al backend

**Done cuando:** un usuario puede registrarse, hacer login, ver el feed,
abrir un artículo y publicar uno propio con imagen.

---

## 5. Fase 2 — Calidad y Robustez (Días 6–7)

**Objetivo:** El código resiste casos de error y es mantenible.

- [ ] Error handling en todos los endpoints (HTTPException estructuradas)
- [ ] Error states en todos los Cubits
- [ ] Loading states y skeleton loaders en la UI
- [ ] Tests básicos de los use cases (mock repositories)
- [ ] Documentación automática en `/docs` (FastAPI OpenAPI)
- [ ] `.env.example` con todas las variables necesarias
- [ ] `README.md` del backend con instrucciones de setup

**Done cuando:** la app no crashea ante errores de red o datos inválidos.

---

## 6. Fase 3 — Extensión (Opcional, si hay tiempo)

**Objetivo:** Demostrar capacidad de overdelivery.

### Rewards Engine básico
- [ ] Colección `read_events` en MongoDB
- [ ] Endpoint `POST /events/read` desde Flutter
- [ ] Score simplificado: tiempo activo + scroll depth
- [ ] Scheduler semanal (script manual o cron)

### Perfil de usuario
- [ ] `ProfileScreen` con estadísticas
- [ ] Historial de artículos leídos

### LLM / RAG (si hay acceso a API)
- [ ] Endpoint `POST /ai/summarize` con contexto del artículo
- [ ] UI básica de chatbot en el detalle del artículo

### Tokenomics visual
- [ ] `TokenCubit` con balance del usuario
- [ ] Badge de tokens en el perfil

---

## 7. Criterios de Calidad Transversales

Estos criterios aplican a todas las fases:

### Backend
- Cada endpoint tiene su schema de request y response
- No hay lógica de negocio en los routers
- Los repositorios son la única interfaz con MongoDB
- Los use cases son testeables sin base de datos

### Flutter
- No hay llamadas HTTP fuera del Data Layer
- No hay lógica de negocio en los widgets
- Los Cubits no conocen los repositorios directamente (pasan por use cases)
- Los widgets son stateless cuando es posible

---

## 8. Dependencias Críticas

```
MongoDB running
    ↓
FastAPI conectado a MongoDB
    ↓
Caddy enrutando al FastAPI
    ↓
Flutter apuntando a la URL de Caddy
    ↓
CRUD funcional
    ↓
Auth JWT
    ↓
Upload de imágenes
```

Cada flecha es un bloqueo: si falla, todo lo que está por encima falla.
Resolver en orden estricto.

---

## 9. Timeline Orientativo

| Día | Foco |
|---|---|
| 1 | Setup completo (docker, MongoDB, FastAPI health check, Flutter base) |
| 2 | Schema + CRUD artículos backend |
| 3 | Auth JWT backend + Domain Layer Flutter con mocks |
| 4 | Presentation Layer Flutter (Cubits + UI screens) |
| 5 | Data Layer Flutter (repositorios reales con dio) |
| 6 | Error handling, edge cases, testing básico |
| 7 | Documentación, README, pulido de UI |
| 8+ | Extensiones opcionales (rewards, LLM, tokenomics) |

---

## 10. Deliverables Finales

- [ ] Backend corriendo con Docker Compose
- [ ] APK compilado y funcional
- [ ] `README.md` con instrucciones de setup para ambos
- [ ] `docs/REPORT.md` con la experiencia y decisiones tomadas
- [ ] Toda la documentación de specs (01–14) completa y coherente
