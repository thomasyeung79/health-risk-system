# Architecture Documentation

> AI Wellness Platform — System Architecture, Data Flow, and Design Decisions

---

## 1. System Overview

The AI Wellness Platform is a **two-tier, API-first** application consisting of a **Streamlit frontend** and a **FastAPI backend**. The frontend communicates with the backend exclusively through a typed HTTP client layer (`api_client/`), never directly accessing databases or business logic modules.

```
                  User Browser (Chrome / Firefox / Edge)
                            │
                            ▼
╔══════════════════════════════════════════════════╗
║              TIER 1: FRONTEND                    ║
║              Streamlit (port 8501)                ║
║                                                   ║
║  HTML/CSS/JS  ◄──  pages/*.py  ◄──  api_client/  ║
║  (rendered by   (5 page           (7 typed        ║
║   Streamlit)    modules)          HTTP clients)    ║
╚═══════════════════════╦═══════════════════════════╝
                        │ HTTP REST + JSON
                        │ http://localhost:8000 (or backend:8000 in Docker)
╔═══════════════════════╩═══════════════════════════╗
║              TIER 2: BACKEND                       ║
║              FastAPI (port 8000)                   ║
║                                                    ║
║  api/ ──► services/ ──► engines/ ──► models/     ║
║        (routes)  (orchestration) (business) (ORM)  ║
╚═══════════════════════╦═══════════════════════════╝
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
╔═══════════════════╗   ╔═══════════════════════════╗
║     SQLite        ║   ║     AI Provider           ║
║   6 tables        ║   ║                           ║
║   79 columns      ║   ║  DeepSeek API ◄── Internet ║
║   Alembic managed  ║   ║     │                     ║
╚═══════════════════╝   ║     ▼                     ║
                        ║  Local Template Fallback   ║
                        ║  (zero cost, no API key)   ║
                        ╚═══════════════════════════╝
```

---

## 2. High-Level Architecture

### Layer Breakdown

```
┌────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  Streamlit                                                   │
│  ├── web_v1.py          — App entry, login, module grid     │
│  ├── pages/0_Login.py   — Register / Login / Logout        │
│  ├── pages/1_Health_Check.py                                │
│  ├── pages/2_Mind_Reset.py                                  │
│  ├── pages/3_Wellness_History.py                            │
│  └── pages/4_Final_Report.py                                │
│                                                              │
│  Legacy fallback (backend unavailable):                      │
│  └── modules/    — Duplicated engines for offline use       │
└────────────────────────────────────────────────────────────┘
        │
        │ api_client/ (typed Python SDK)
        │
┌────────────────────────────────────────────────────────────┐
│                    API LAYER                                 │
│  FastAPI routers (app/api/)                                  │
│  ├── auth.py     — /api/v1/auth/*                           │
│  ├── health.py   — /api/v1/health/*                         │
│  ├── emotion.py  — /api/v1/emotion/*                        │
│  ├── report.py   — /api/v1/reports/*                        │
│  └── trend.py    — /api/v1/trends/*                         │
│                                                              │
│  Authentication: FastAPI Depends(get_current_user)           │
│    → 401 on missing/invalid/expired JWT                      │
│    → 404 on user_id mismatch (user isolation)                │
└────────────────────────────────────────────────────────────┘
        │
┌────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                              │
│  Business logic orchestration (app/services/)                │
│  ├── auth.py              — bcrypt, JWT, token management   │
│  ├── health_check.py      — 8 engines → overall scoring     │
│  ├── emotion_analysis.py  — reflection engine → DB persist  │
│  ├── health_analyzer.py   — risk scoring, interactions      │
│  └── report_engine/       — AI report pipeline              │
│       ├── report_service.py  — cache → context → provider   │
│       ├── context_builder.py — health+emotion → LLM input   │
│       ├── provider.py        — provider factory             │
│       ├── deepseek_provider.py                               │
│       ├── local_provider.py  — template-based fallback      │
│       ├── cache.py           — same-day cache logic         │
│       ├── prompts.py         — system + user prompt templ.  │
│       └── response_parser.py — LLM output → sections        │
│   ─────────────────────                                       │
│  Trend analysis (app/services/trend_engine/)                  │
│   ├── trend_service.py     — summary orchestration          │
│   ├── metric_analyzer.py   — per-metric trend computation   │
│   └── config.py            — thresholds, metric definitions │
└────────────────────────────────────────────────────────────┘
        │
┌────────────────────────────────────────────────────────────┐
│                    ENGINE LAYER (business logic)             │
│  Pure functions, no side effects (app/engines/)             │
│  ├── bmi.py          — BMI calculation                     │
│  ├── water_ratio.py  — Hydration assessment                │
│  ├── sleep.py        — Sleep quality scoring               │
│  ├── activity.py     — Activity level scoring              │
│  ├── diet.py         — Diet quality scoring                │
│  ├── mental_healthy.py                                     │
│  ├── screen_time.py                                        │
│  ├── habit.py                                               │
│  └── emotion.py      — 10 functions from reflection_engine │
└────────────────────────────────────────────────────────────┘
        │
┌────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  SQLAlchemy ORM + SQLite (app/models/)                      │
│  ├── base.py             — DeclarativeBase + TimestampMixin │
│  ├── user.py             — users table                     │
│  ├── refresh_token.py    — refresh_tokens table            │
│  ├── health_record.py    — health_records (43 columns)     │
│  ├── emotion_record.py   — emotion_records (15 columns)    │
│  └── report_record.py    — report_records (16 columns)     │
│                                                              │
│  Migrations: Alembic (alembic/versions/                     │
│    001 → 002 → 003 → 004)                                   │
└────────────────────────────────────────────────────────────┘
```

---

## 3. Request Flow

### Health Check Example

```
User fills form → clicks "Generate"
        │
        ▼
pages/1_Health_Check.py
        │
        ▼
health_api.check(**form_data)
        │
        ├── ApiClient.build_headers() → Authorization: Bearer <jwt>
        ├── POST /api/v1/health/check
        │
        ▼
api/health.py → post_health_check()
        │
        ├── Depends(get_current_user) → JWT verification
        │     ├── Extract Bearer token
        │     ├── Decode with JWT_SECRET
        │     ├── Check token type == "access"
        │     ├── Load user from DB
        │     └── Return User or raise 401
        │
        ├── Depends(get_db) → SQLAlchemy session
        │
        ▼
services/health_check.py → run_health_check(user_id, **data)
        │
        ├── Engine Layer: calc_bmi(), calc_sleep(), … (8 calls)
        ├── Service Layer: calculate_overall_result()
        │     ├── Sum 8 module scores
        │     ├── Compute 8 pair interactions
        │     ├── Apply thresholds → risk level
        │     └── Build priority focus + action plan
        │
        ├── ORM: HealthRecord(user_id=..., **scores).save()
        │
        ▼
Return JSON Response
        │
        ▼
_adapt_api_response() → convert to legacy format
        │
        ▼
Render Streamlit: metrics + expanders + radar chart
```

---

## 4. Authentication Flow (JWT)

### Registration

```
Client                          Server
  │                                │
  │  POST /api/v1/auth/register    │
  │  {username, password}          │
  │                                ├── Check uniqueness (409 if exists)
  │                                ├── hash_password(password) → bcrypt
  │                                ├── User.create(username, hash)
  │                                └── 201 → UserResponse
  │◄─  {id, username, created_at} │
```

### Login + Token Issue

```
Client                          Server
  │                                │
  │  POST /api/v1/auth/login       │
  │  {username, password}          │
  │                                ├── User.query(username)
  │                                ├── verify_password(password, hash)
  │                                ├── create_access_token(user_id)
  │                                │     └── JWT(sub=user_id, type=access, exp=30m)
  │                                ├── create_refresh_token(user_id)
  │                                │     └── JWT(sub=user_id, type=refresh, jti=uuid, exp=7d)
  │                                ├── RefreshToken.create(user_id, jti, exp)
  │                                └── 200 → {access_token, refresh_token, user}
  │◄─  {tokens, user}
  │
  ├── api_client.set_tokens()
  └── session_state["access_token"] = token
```

### Authenticated Request (api_client)

```
Client                          Server
  │                                │
  │  GET /api/v1/health/stats      │
  │  Authorization: Bearer <jwt>   │
  │                                │
  │                                ├── decode_token(jwt)
  │                                │     ├── Valid → payload
  │                                │     └── Invalid/Expired → 401
  │◄─  200 / 401                   │
  │                                │
  │  ┌─ 401 → client._try_refresh()│
  │  │       POST /auth/refresh   │
  │  │        {refresh_token}     │
  │  │        ├── decode refresh   │
  │  │        ├── check revoked    │
  │  │        ├── revoke old       │
  │  │        └── issue new pair   │
  │  │                              │
  │  │       Retry original request│
  │  └─────────────────────────────│
```

### Logout

```
Client                          Server
  │                                │
  │  POST /api/v1/auth/logout      │
  │  {refresh_token}               │
  │                                ├── decode refresh
  │                                ├── RefreshToken.revoke(jti)
  │                                └── 200
  │◄─  {message: "Logged out"}    │
  │
  └── client.clear_tokens()
```

---

## 5. Database Design

### Entity Relationship Summary

```
users (1) ─────< refresh_tokens (M)
  │
  │ (1)────< health_records  (M)
  │
  │ (1)────< emotion_records (M)
  │
  └──── (1)────< report_records (M)
```

### Table Definitions

#### users
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | User ID |
| created_at | DATETIME | NOT NULL | Registration time |
| username | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Login identifier |
| display_name | VARCHAR(100) | NULLABLE | Display name |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash |
| preferred_language | VARCHAR(10) | DEFAULT 'English' | User language |
| is_active | BOOLEAN | DEFAULT 1 | Account status |

#### refresh_tokens
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK | Token ID |
| user_id | INTEGER | FK → users.id | Token owner |
| token_jti | VARCHAR(36) | UNIQUE, INDEX | JWT ID |
| expires_at | DATETIME | NOT NULL | Expiry timestamp |
| revoked | BOOLEAN | DEFAULT 0 | Revocation flag |
| created_at | DATETIME | NOT NULL | Creation time |

#### health_records (42 + 1 columns)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Record ID |
| user_id | INTEGER | FK → users.id |
| created_at | DATETIME | Assessment time |
| language | VARCHAR(10) | Assessment language |
| weight_kg / height_cm / water_l / … | FLOAT | Raw inputs (22 fields) |
| bmi_score / water_score / … | INTEGER | Module scores (0-3) |
| health_score | FLOAT | Overall (0-100) |
| risk_percent | FLOAT | Risk percentage |
| risk_level | VARCHAR(20) | healthy/low/medium/high |
| primary_focus | TEXT | Priority area |
| action_plan | TEXT | Action items (pipe-delimited) |

#### emotion_records (14 + 1 columns)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Record ID |
| user_id | INTEGER | FK → users.id |
| mood_key | VARCHAR(20) | Calm/Tired/Anxious/Low/Angry/Numb |
| event_key | VARCHAR(30) | Life event |
| energy | INTEGER | 1-10 |
| stress | INTEGER | 1-10 |
| pattern_key | VARCHAR(30) | Emotional pattern |
| pattern_severity | VARCHAR(10) | High/Medium/Low |
| summary / tonight / tomorrow | TEXT | Generated text |
| breathing_type | VARCHAR(20) | calming/pause/recovery/basic |
| full_story | TEXT | Complete narrative |

#### report_records (15 + 1 columns)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Report ID |
| user_id | INTEGER | FK → users.id |
| style | VARCHAR(20) | balanced/coaching/clinical |
| provider | VARCHAR(20) | deepseek/local |
| model | VARCHAR(30) | deepseek-chat/template |
| summary / sections / raw_output | TEXT | Report content |
| tokens_used | INTEGER | Token count |
| latency_ms | INTEGER | Generation time |
| is_cached | BOOLEAN | Cache hit indicator |
| is_fallback | BOOLEAN | Fallback indicator |

### Migration History

| Migration | Description |
|-----------|-------------|
| 001 | Create health_records |
| 002 | Create emotion_records |
| 003 | Create report_records |
| 004 | Create users + refresh_tokens + add user_id |

---

## 6. AI Report Pipeline

```
                    ┌──────────────────────┐
                    │  GET /api/v1/reports/ │
                    │     generate          │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  1. Check Cache       │
                    │  (same day + lang +   │
                    │   style + provider)   │
                    │                       │
                    │  HIT ──► Return cached │
                    │  MISS ──► Continue     │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  2. Context Builder   │
                    │  (zero API calls)     │
                    │                       │
                    │  Latest health_record  │
                    │  Latest emotion_record │
                    │  Recent trends (7d)    │
                    │  Flags + correlations  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  3. Provider Selection │
                    │                       │
                    │  DEEPSEEK_API_KEY?    │
                    │   ├── Yes ──► DeepSeek│
                    │   └── No  ──► Local   │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  4. LLM Call          │
                    │  (or local template)  │
                    │                       │
                    │  System prompt        │
                    │  + User context        │
                    │  + Style instruction   │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  5. Response Parser   │
                    │                       │
                    │  Parse ## sections    │
                    │  Fallback to plain    │
                    │  text if no headings  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  6. Persist + Return  │
                    │                       │
                    │  Save to report_records│
                    │  Record tokens +       │
                    │  latency + is_fallback │
                    └──────────────────────┘
```

### Cache Strategy

```
Cache Key: {today} | {language} | {style} | {provider}
TTL: End of day (midnight UTC)
Storage: report_records table (is_cached flag)

Cache Hit:    Return immediately, < 10ms, 0 tokens
Cache Miss:   Generate new → persist → return
```

### Provider Fallback Chain

```
create_provider()
    │
    ├── DEEPSEEK_API_KEY set? ──► DeepSeekProvider
    │
    └── No API key ──► LocalProvider (template, zero cost)

generate_report()
    │
    ├── provider.generate() succeeds ──► Return result
    │
    └── provider.generate() fails ──► LocalProvider fallback
        is_fallback = True
```

---

## 7. Trend Analysis Pipeline

```
GET /api/v1/trends/summary?days=7
        │
        ▼
trend_service.compute_summary(user_id, days)
        │
        ├── Count health_records (user_id, >= cutoff)
        ├── Count emotion_records (user_id, >= cutoff)
        │
        ▼
For each metric [health_score, stress, energy, sleep_score]:
        │
        ▼
metric_analyzer.compute_metric_trend(user_id, metric, days)
        │
        ├── Query records (user_id, created_at >= cutoff, ASC)
        ├── current = values[-1], previous = values[0]
        ├── change = current - previous
        │
        └── Determine direction:
              │
              ├── |change| < threshold ──► "stable"
              │
              ├── higher_is_better=True:
              │     ├── change > 0 ──► "improving"
              │     └── change < 0 ──► "declining"
              │
              └── higher_is_better=False:
                    ├── change < 0 ──► "improving"
                    └── change > 0 ──► "declining"
```

### Thresholds

| Metric | Threshold | higher_is_better |
|--------|-----------|-----------------|
| health_score | ±5.0 | True |
| stress | ±1.5 | False |
| energy | ±1.5 | True |
| sleep_score | ±1.0 | False |

---

## 8. Docker Architecture

### Container Topology

```
┌─ docker-compose.yml ──────────────────────────────────────┐
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │  frontend            │    │  backend                    │ │
│  │  Dockerfile          │    │  backend/Dockerfile         │ │
│  │  python:3.12-slim    │    │  python:3.12-slim           │ │
│  │                      │    │                             │ │
│  │  Port: 8501          │    │  Port: 8000                 │ │
│  │  Health: /_stcore/   │    │  Health: /health            │ │
│  │         health       │    │                             │ │
│  │                      │    │  Volume: sqlite_data:/app/  │ │
│  │  Env:                │    │         backend/data        │ │
│  │  API_BASE_URL=http://│    │                             │ │
│  │  backend:8000        │    │  Env: DEEPSEEK_API_KEY,     │ │
│  │                      │    │       JWT_SECRET, …         │ │
│  └─────────┬───────────┘    └──────────┬──────────────────┘ │
│            │                            │                   │
│            │  depends_on: backend       │                   │
│            │  (condition: healthy)      │                   │
│            └──────────────┬─────────────┘                   │
│                           │                                 │
│                    http://backend:8000                       │
│                   (Docker internal DNS)                     │
└─────────────────────────────────────────────────────────────┘
```

### Volume Strategy

```yaml
volumes:
  sqlite_data:
    # Local Docker: data persists in named volume
    # Railway/Render: not persistent (use PostgreSQL for cloud)
```

### Startup Sequence

```
1. docker compose up
2. Backend container starts
3. FastAPI lifespan: Base.metadata.create_all()
4. Backend health check passes (≈10s)
5. Frontend container starts
6. api_client connects to http://backend:8000
7. Frontend health check passes (≈15s)
8. System ready
```

---

## 9. Security Design

### Authentication

| Measure | Implementation |
|---------|---------------|
| **Password Storage** | bcrypt (via passlib, 12 rounds) |
| **Access Token** | JWT (HS256), 30-minute expiry |
| **Refresh Token** | JWT + DB persistence, 7-day expiry |
| **Token Revocation** | Refresh token stored in DB; revoke on logout |
| **Comparison** | Constant-time (hmac.compare_digest) |

### User Isolation

| Layer | Mechanism |
|-------|-----------|
| **API** | `get_current_user` dependency on all protected endpoints |
| **Service** | `user_id` parameter on all service functions |
| **ORM** | `.filter(Record.user_id == current_user.id)` on all queries |
| **Error** | 404 (not 403) on cross-user access — hides record existence |

### Data Protection

| Concern | Status |
|---------|--------|
| **API Keys** | Read from environment variables, not hardcoded |
| **Secrets in Git** | `.env` in `.gitignore`, `.env.example` committed |
| **XSS** | Streamlit's default markdown rendering is safe; `escape()` used on custom HTML |
| **SQL Injection** | SQLAlchemy ORM + parameterized queries |
| **CORS** | FastAPI CORS middleware (allow all origins for dev) |
| **Rate Limiting** | Not yet implemented (planned for production) |

---

## 10. Design Decisions

### Why FastAPI over Django/Flask?

| Criterion | FastAPI | Django | Flask |
|-----------|---------|--------|-------|
| Learning curve | Low | High | Low |
| Auto docs | ✅ OpenAPI | ❌ (DRF) | ❌ |
| Async support | ✅ Native | ⚠️ (3.0+) | ❌ |
| API-first design | ✅ Native | ❌ Monolithic | ⚠️ |
| Project size | ✅ 183 tests | ❌ Overkill | ✅ |
| **Decision** | **✅** | — | — |

### Why SQLite over PostgreSQL?

| Criterion | SQLite | PostgreSQL |
|-----------|--------|-----------|
| Setup time | Zero | 15 min + Docker |
| Development speed | Instant | Requires migration |
| Single-user performance | Excellent | Excellent |
| Concurrent writes | Poor | Excellent |
| **Stage** | **✅ Development** | **⬅️ Future** |

### Why Streamlit over Next.js?

| Criterion | Streamlit | Next.js |
|-----------|-----------|---------|
| Python-only | ✅ Yes | ❌ Requires JS |
| Speed to MVP | Days | Weeks |
| Data apps | ✅ Excellent | ❌ Mediocre |
| UI polish | ❌ Basic | ✅ Excellent |
| **Stage** | **✅ MVP** | **⬅️ Future** |

### Why DeepSeek over OpenAI?

| Criterion | DeepSeek | OpenAI |
|-----------|----------|--------|
| Cost per 1K tokens | $0.00014 | $0.15 |
| China accessibility | ✅ Yes | ❌ No |
| API compatibility | ✅ OpenAI-compatible | ✅ Native |
| Quality | ⚠️ Good | ✅ Excellent |
| **Decision** | **✅ Default** | **⬅️ Optional** |

---

## 11. Current Limitations

### Architectural

| Limitation | Impact | Planned Solution |
|------------|--------|-----------------|
| **SQLite** | No concurrent write support | PostgreSQL (Phase B) |
| **Streamlit** | Not a professional frontend framework | Next.js (Phase D) |
| **No Live Deployment** | Local access only | VPS / Railway (Phase B) |
| **No Rate Limiting** | No brute-force protection | SlowAPI / middleware (Phase B) |

### Code Quality

| Debt | Location | Plan |
|------|----------|------|
| Legacy `modules/` engine duplicates | `AI_Wellness_Platform/modules/` | Move to `legacy/` or delete |
| `generate_final_report()` dead code | `pages/4_Final_Report.py` | Remove in cleanup phase |
| `database.py` fallback code | `AI_Wellness_Platform/` | Remove after backend validation |

---

## 12. Future Evolution Path

```
Current (MVP)                     Phase B (Next)                  Phase C-D (Future)
┌────────────────────┐           ┌────────────────────┐          ┌────────────────────┐
│                    │           │                    │          │                    │
│  Streamlit         │    ──►    │  Streamlit         │   ──►   │  Next.js           │
│  SQLite            │           │  PostgreSQL         │         │  PostgreSQL         │
│  Local Docker      │           │  Live Deploy        │         │  Mobile Responsive  │
│  202 tests         │           │  Warning Engine     │         │  PWA               │
│  EN + CN           │           │  Correlation        │         │  한국어            │
│                    │           │  1,000+ tests       │         │  Commercial        │
└────────────────────┘           └────────────────────┘          └────────────────────┘
```

---

*Document version: 1.0 — Last updated: 2026-06-08*
*Accompanies AI Wellness Platform Backend v0.1.0*
