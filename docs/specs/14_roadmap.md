# 14_ROADMAP.md - Symmetry (InfoVeraz)

## 1. Propósito
Este documento define el progreso de implementación y la visión futura del sistema Symmetry. Se estructura en fases incrementales basadas en la estabilidad del núcleo antes de escalar a capas de incentivos.

---

## 2. Estado Actual del Proyecto: **Híbrido Consolidado**

| Fase | Estado | Descripción |
|---|---|---|
| **Fase 0: Setup** | ✅ COMPLETADA | Gradle 8.14, AGP 8.11.1, Kotlin 2.2.20. Entorno estable. |
| **Fase 1: MVP & Auth** | ✅ COMPLETADA | Firebase Auth integrado. CRUD funcional (FastAPI + Mongo). |
| **Fase 2: Robustez & AI** | ✅ COMPLETADA | Fallback de Firestore. Chatbot con redundancia (OpenAI Fallback). |
| **Fase 3: Economía & Verificación**| 🚀 PRÓXIMAMENTE | Rewards Engine, Tokenomics y Sistema de Reputación. |

---

## 3. Fase 0 — Infraestructura Moderna (Completada)
**Objetivo:** Toolchain de última generación para evitar deuda técnica.
- [x] Actualización a **Gradle 8.14** y **AGP 8.11.1**.
- [x] Optimización de `gradle.properties` (3GB Heap, Built-in Kotlin).
- [x] Migración a `ionicons: ^0.2.2` y `flutter_markdown_plus: ^1.0.7`.

## 4. Fase 1 — Identidad y Publicación (Completada)
**Objetivo:** Autenticación real y persistencia de contenido verificable.
- [x] **Firebase Auth**: Implementación de Repositorio, Cubit y UI (Cyber Night).
- [x] **Onboarding Experience**: Pantalla de bienvenida con animación `Cyber Pulse`.
- [x] **Real Image Upload**: Integración de `FirebaseStorage` segmentado por `userId`.
- [x] **Auth Authoring**: Artículos vinculados a autores reales para trazabilidad.

## 5. Fase 2 — Alta Disponibilidad e IA (Completada)
**Objetivo:** Resiliencia ante fallos y asistente inteligente de vanguardia.
- [x] **Hybrid Data Source**: Fallback automático de FastAPI a Cloud Firestore.
- [x] **Asistente Owl**: Integración con Ollama (Qwen 2.5b) local.
- [x] **Redundancia AI (OPAD Style)**: Fallback dinámico a **OpenAI (GPT-4o-mini)** vía `.env`.
- [x] **Error Handling**: Manejo de timeouts y estados de error en Cubits.

## 6. Fase 3 — Economía del Contenido (Próximos Pasos)
**Objetivo:** Incentivar la veracidad y el consumo de información de calidad.

### Rewards Engine
- [ ] Implementación de `RewardsRepository`.
- [ ] Tracking de eventos de lectura (Scroll, Time-on-page).
- [ ] Cálculo de recompensas basado en verificación de autor.

### Tokenomics Visual
- [ ] `TokenCubit` para gestión de balance (`SYM` tokens).
- [ ] Pantalla de perfil con historial de recompensas.

### Sistema de Reputación
- [ ] Badge de "Periodista Verificado".
- [ ] Algoritmo de confianza basado en trackrecord de publicaciones.

---

## 7. Criterios de Calidad Transversales

### Frontend (Clean Architecture)
- Los Repositorios actúan como orquestadores de múltiples fuentes de datos (Hybrid).
- Los Cubits gestionan estados de carga y error consistentemente.
- La estética **Cyber Night** es la norma visual del proyecto.

### Seguridad
- Gestión de secretos mediante `.env` (nunca en control de versiones).
- Reglas de Firebase Storage para proteger la multimedia por `userId`.
