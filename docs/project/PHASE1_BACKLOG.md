# Fase 1 — Backlog (MVP assignment + stub de recompensas)

Este documento acota el trabajo de la **primera fase de implementación** tras el setup ([14_roadmap.md](Spec_workflows/14_roadmap.md) Fases 0–1) y las decisiones del [ADR 001](ADR_001_prototype_rest_mongo_vs_firestore.md).

## Objetivo

Entregar el **MVP del assignment** (flujo periodista: registro/login, listado, detalle, creación de artículos con imagen cuando aplique) sobre el **prototipo REST + MongoDB + JWT**, más un **stub mínimo** de recompensas basado en eventos de lectura persistidos **sin** economía de tokens completa.

## Criterios de hecho (done)

### Backend (`api/`)

- [ ] `GET /health` responde 200 con cuerpo JSON estable.
- [ ] MongoDB conectado (Motor); variables documentadas en `api/.env.example`.
- [ ] **Artículos:** CRUD mínimo acordado con el cliente (`GET` lista/paginación, `GET` por id, `POST` crear; `PATCH`/`DELETE` si el MVP lo exige).
- [ ] **Auth:** `POST /auth/register`, `POST /auth/login` devolviendo JWT; rutas protegidas donde corresponda.
- [ ] **Upload:** endpoint de thumbnail o URL de imagen coherente con Flutter (según diseño de [05_CONTENT_PIPELINE.md](Spec_workflows/05_CONTENT_PIPELINE.md)).
- [ ] **Stub recompensas:** `POST /events/read` (o nombre equivalente) que persista un documento en colección `read_events` con `user_id`, `article_id`, marca temporal y campos opcionales (`dwell_ms`, `scroll_ratio`) — **sin** calcular pool semanal ni emitir tokens.

### Flutter (`frontend/`)

- [ ] Cliente HTTP (`dio`) configurado con base URL del entorno (local / emulador Android `10.0.2.2`).
- [ ] Capa **Data** contra la API para artículos y auth; Domain/Presentation alineados con Clean Architecture existente.
- [ ] Pantallas/uso del assignment funcionando contra el prototipo **sin depender de Firebase** en esta fase (Firebase puede quedar desactivado o no usado en rutas MVP; decisión técnica documentada en README).
- [ ] Envío de al menos un evento de lectura de prueba al stub desde la pantalla de detalle (o hook mínimo).

### Calidad mínima

- [ ] Errores de red y 401 gestionados sin crashear la app.
- [ ] Instrucciones en `README` raíz o `api/README.md` para levantar Docker + ejecutar Flutter.

## Fuera de alcance en Fase 1

| Tema | Motivo |
|------|--------|
| Tokenomics y emisión ([01](Spec_workflows/01_tokenomics.md), [02](Spec_workflows/02_emission_model.md)) | Extensión; no bloquea MVP |
| Motor completo de rewards ([03](Spec_workflows/03_rewards_engine.md)) | Solo stub de eventos |
| Antifraude avanzado ([04](Spec_workflows/04_ANTIFRAUD.md)) | Modo degradado; ver §1.1 del spec |
| LLM / RAG ([06](Spec_workflows/06_LLM_RAG.md)) | Opcional posterior |
| Sesgo / fiabilidad ([07](Spec_workflows/07_BIAS_RELIABILITY.md)) | Opcional posterior |
| Gobernanza / publicidad ([08](Spec_workflows/08_governance.md), [09](Spec_workflows/09_advertising_economy.md)) | Fuera de MVP |
| Port a Firestore | Fase D ([ADR 001](ADR_001_prototype_rest_mongo_vs_firestore.md)) |
| Dashboards y métricas completas ([13](Spec_workflows/13_metrics.md)) | Health + logs básicos bastan |

## Orden sugerido de implementación

1. Fase A ya completada: compose, API `/health`, Flutter + `dio` verificando backend.
2. Schema Mongo (`articles`, `users`) e índices ([12_data_model.md](Spec_workflows/12_data_model.md)).
3. CRUD + auth end-to-end en API y app.
4. Stub `read_events` + una métrica derivada trivial (opcional: contador en `articles`).

## Referencias

- [14_roadmap.md](Spec_workflows/14_roadmap.md)
- [11_backend_architecture.md](Spec_workflows/11_backend_architecture.md)
- [12_data_model.md](Spec_workflows/12_data_model.md)
