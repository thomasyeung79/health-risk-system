# AI Wellness Backend

FastAPI backend for the AI Wellness Platform — a bilingual (English/中文) health and emotion management system.

[![Backend CI](https://github.com/thomasyeung79/health-risk-system/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/thomasyeung79/health-risk-system/actions/workflows/backend-ci.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) 0.136+ |
| Database | SQLite (via SQLAlchemy 2.0 + Alembic) |
| Validation | Pydantic v2 |
| Authentication | JWT (python-jose) + bcrypt |
| AI Provider | DeepSeek + Local Template Fallback |
| Testing | pytest + httpx TestClient |

---

## Quick Start

### Prerequisites

- Python 3.12+

### 1. Setup

```bash
cd AI_Wellness_Platform/backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env
```

### 2. Run database migration

```bash
alembic upgrade head
```

Creates `data/ai_wellness.db` with **6 tables** (users, refresh_tokens, health_records, emotion_records, report_records).

### 3. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Verify

```bash
curl http://localhost:8000/health
# => {"status":"ok","version":"0.1.0"}

open http://localhost:8000/docs
```

---

## Running Tests

```bash
pytest -v                 # All 183 tests
python scripts/check_backend.py  # Health verification
```

---

## API Endpoints (14 total)

All data endpoints require JWT via `Authorization: Bearer <token>`.

### Status

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | API health check |

### Authentication (`/api/v1/auth`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/register` | Register new user |
| `POST` | `/auth/login` | Login, returns JWT pair |
| `POST` | `/auth/refresh` | Refresh access token |
| `POST` | `/auth/logout` | Revoke refresh token |
| `GET` | `/auth/me` | Current user profile |

### Health Check (`/api/v1/health`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/health/check` | Run full health assessment (8 modules) |
| `GET` | `/health/records` | List health records (paginated) |
| `GET` | `/health/records/{id}` | Get single record |
| `GET` | `/health/stats` | Aggregated health statistics |

### Emotion Analysis (`/api/v1/emotion`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/emotion/analyze` | Run emotion analysis |
| `GET` | `/emotion/records` | List emotion records |
| `GET` | `/emotion/records/{id}` | Get single record |
| `GET` | `/emotion/stats` | Aggregated emotion statistics |

### Wellness Report (`/api/v1/reports`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/reports/generate` | Generate AI wellness report |
| `GET` | `/reports` | List generated reports |
| `GET` | `/reports/{id}` | Get single report |

### Trend Analysis (`/api/v1/trends`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/trends/summary` | Trend summary for core metrics |

---

## Database (6 tables)

| Table | Columns | Description |
|-------|---------|-------------|
| `users` | 7 | User accounts with bcrypt password hashes |
| `refresh_tokens` | 6 | JWT refresh token persistence |
| `health_records` | 43 | Health assessment data |
| `emotion_records` | 15 | Emotion analysis data |
| `report_records` | 16 | AI report cache |

---

## Project Structure

```
backend/
├── Dockerfile
├── pyproject.toml
├── alembic.ini
│
├── app/
│   ├── main.py                # Entry point
│   ├── config.py              # Settings
│   ├── database.py            # Engine + session
│   │
│   ├── models/                # 5 ORM models
│   ├── schemas/               # 6 Pydantic modules
│   ├── api/                   # 5 route modules
│   ├── services/              # Auth + Health + Emotion + Report Engine + Trend Engine
│   ├── engines/               # 9 business logic modules
│   └── tests/                 # 183 tests (17 files)
│
├── alembic/versions/          # 4 migration scripts
├── scripts/check_backend.py   # Health verification
└── data/                      # SQLite database
```

---

## Authentication

- **Password hashing**: bcrypt (12 rounds)
- **Access token**: JWT (HS256, 30 min expiry)
- **Refresh token**: JWT + DB persistence (7 day expiry)
- **User isolation**: All data filtered by `user_id` at ORM + API + Service layers

---

## AI Report Pipeline

```
Request → Cache check → Context Builder → Provider (DeepSeek/Local) → Parse → Persist
```

- Auto-fallback to local templates when no API key is configured
- Same-day cache avoids redundant AI calls

---

## Trend Analysis

4 core metrics over configurable windows (default 7 days):

| Metric | Source | Range | Threshold |
|--------|--------|-------|-----------|
| health_score | health_records | 0-100 | ±5.0 |
| stress | emotion_records | 1-10 | ±1.5 |
| energy | emotion_records | 1-10 | ±1.5 |
| sleep_score | health_records | 0-3 | ±1.0 |

---

## Development Status

**Complete**: Health assessment, emotion analysis, AI reports, trend analysis, JWT auth, user isolation, Docker Compose, CI (183 tests)

**Next**: Correlation analysis, warning engine, PostgreSQL migration

See [CHANGELOG.md](CHANGELOG.md) and [docs/architecture.md](../docs/architecture.md) for details.

---

## Language Support

- `"English"` and `"中文"` supported on all endpoints
- All diagnostic texts and reports are bilingual
