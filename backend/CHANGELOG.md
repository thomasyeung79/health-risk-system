# Changelog

All notable changes to the AI Wellness Backend will be documented in this file.

---

## [0.1.0] — 2026-06-07

### Step 1: Project Skeleton

- Initialized `backend/` directory structure
- Created `pyproject.toml` with FastAPI + SQLAlchemy + Alembic dependencies
- Added `.env.example` and `.gitignore`
- Set up package discovery for `app/` directory

**Files created:** 12 (package init files + config files)

---

### Step 2: Database Layer

- Added `app/config.py` — pydantic-settings configuration
- Added `app/database.py` — SQLAlchemy engine + session factory + `get_db` dependency
- Added `app/models/base.py` — ORM `Base` + `TimestampMixin`
- Added `app/models/health_record.py` — `HealthRecord` model (42 columns)
- Added `alembic.ini` + `alembic/env.py` + `alembic/script.py.mako`
- Added `alembic/versions/001_create_health_records.py` — initial migration
- Added `app/tests/conftest.py` — in-memory SQLite test fixture
- Added `app/tests/test_conftest.py` — fixture verification tests

**Verification:** Python imports OK, table creation OK (42 columns), insert/query OK

---

### Step 3: Health Check Engine Migration

- Migrated 8 assessment engines from `modules/` to `backend/app/engines/`:
  - `bmi.py`, `water_ratio.py`, `sleep.py`, `activity.py`
  - `diet.py`, `mental_healthy.py`, `screen_time.py`, `habit.py`
- Migrated `health_analyzer.py` to `backend/app/services/health_analyzer.py`
- Created `backend/app/services/health_check.py` — orchestration service
- All engines use top-level imports from shared `LEVEL_TEXTS`
- Chinese language support preserved in all engines
- Created comprehensive tests:
  - **engines:** 23 tests covering all risk levels
  - **analyzer:** 9 tests (dedup, levels, overall, priority focus, Chinese output)
  - **health_check:** 4 tests (full check, persistence, high risk, Chinese)

**Verification:** 35/35 tests passed

---

### Step 4: FastAPI API Layer

- Added `app/main.py` — FastAPI entry point with CORS, lifespan, route registration
- Added `app/api/router.py` — central route registration
- Added `app/api/health.py` — 5 health check endpoints
- Added `app/schemas/common.py` — shared Pydantic models
- Added `app/schemas/health.py` — 9 request/response schemas
- Added `app/tests/test_api_health.py` — 11 API integration tests

**Endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | API status check |
| POST | `/api/v1/health/check` | Run full health assessment |
| GET | `/api/v1/health/records` | List records with pagination |
| GET | `/api/v1/health/records/{id}` | Single record detail |
| GET | `/api/v1/health/stats` | Aggregated statistics |

**Verification:** 47/47 tests passed

---

### Step 5: Migration Verification & Documentation

- Verified Alembic migration from scratch (`alembic upgrade head`)
- Confirmed 42-column health_records table
- Confirmed ORM insert/query works end-to-end
- Added `README.md` — complete setup and usage documentation
- Added `CHANGELOG.md` — this file
- Added `scripts/check_backend.py` — backend health verification script

**Verification:** 47/47 tests passed, migration verified, check script passes

---

### Step 6: Emotion Analysis Module Migration

- Created `app/models/emotion_record.py` — EmotionRecord model (15 columns)
- Created `alembic/versions/002_create_emotion_records.py` — migration script
- Migrated `modules/reflection_engine.py` to `app/engines/emotion.py` — 10 functions preserved
- Created `app/services/emotion_analysis.py` — orchestration service
- Created `app/schemas/emotion.py` — 9 Pydantic models
- Created `app/api/emotion.py` — 4 emotion analysis endpoints
- Registered emotion routes in `app/api/router.py`
- Created tests:
  - **emotion engine:** 27 tests (pattern detection, topic selection, breathing, guidance)
  - **emotion analysis:** 3 tests (full analysis, DB persistence, Chinese output)
  - **API emotion:** 9 tests (analyze, list, get, stats, validation, 404, Chinese)
- All Chinese language support preserved
- Zero changes to old Streamlit project

**Verification:** 84/84 tests passed

---

### Step 7: Documentation & E2E Verification

- Updated `README.md` — emotion module docs, 9 API endpoints, 84 tests, project structure
- Updated `CHANGELOG.md` — complete Step 6 + Step 7 records
- Updated `scripts/check_backend.py` — emotion_records table + emotion API checks
- Added `app/tests/test_e2e.py` — end-to-end health + emotion full flow tests
- Alembic migration verified from scratch (2 tables, 57 total columns)
- Zero changes to old Streamlit project

**Verification:** 84/84 tests passed, check script passes, e2e tests pass

---

## Planned

| Step | Content |
|------|---------|
| Step 8 | User authentication (JWT) |
| Step 9 | AI report integration (OpenAI/DeepSeek) |
| Step 10 | Docker Compose |
| Step 11 | Frontend (Next.js) |
