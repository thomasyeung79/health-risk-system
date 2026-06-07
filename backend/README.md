# AI Wellness Backend

FastAPI backend for the AI Wellness Platform — a bilingual (English/中文) health and emotion management system.

This is the backend API for the [AI Wellness Platform](https://github.com/thomasyeung79/health-risk-system).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) 0.136+ |
| Database | SQLite (via SQLAlchemy 2.0 + Alembic) |
| Validation | Pydantic v2 |
| Testing | pytest + httpx TestClient |

## Quick Start

### Prerequisites

- Python 3.12+

### 1. Clone and enter backend

```bash
cd AI_Wellness_Platform/backend
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

- **Windows**: `.venv\Scripts\activate`
- **macOS/Linux**: `source .venv/bin/activate`

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Configure environment

```bash
cp .env.example .env
```

Default `.env` is ready for local development — no changes needed.

### 5. Run database migration

```bash
alembic upgrade head
```

This creates `data/ai_wellness.db` with all tables.

### 6. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

### 7. Verify

```bash
# Health check
curl http://localhost:8000/health
# => {"status":"ok","version":"0.1.0"}

# Swagger UI (open in browser)
open http://localhost:8000/docs
```

## Running Tests

```bash
# All tests
pytest -v

# Specific test file
pytest app/tests/test_analyzer.py -v

# With coverage
coverage run -m pytest && coverage report -m
```

Expected result: **84 passed**

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | API status check |
| `POST` | `/api/v1/health/check` | Run a full health assessment |
| `GET` | `/api/v1/health/records` | List health records (pagination via `?limit=&offset=`) |
| `GET` | `/api/v1/health/records/{id}` | Get a single record (404 if not found) |
| `GET` | `/api/v1/health/stats` | Aggregated statistics |
| `POST` | `/api/v1/emotion/analyze` | Run emotion analysis |
| `GET` | `/api/v1/emotion/records` | List emotion records (pagination) |
| `GET` | `/api/v1/emotion/records/{id}` | Get a single emotion record |
| `GET` | `/api/v1/emotion/stats` | Aggregated emotion statistics |

Interactive docs: http://localhost:8000/docs (Swagger UI)

### POST /api/v1/health/check — Example

```json
{
  "language": "English",
  "weight_kg": 70.0,
  "height_cm": 175.0,
  "water_l": 2.0,
  "situation": "A",
  "thirst_level": "A",
  "urine_color": "A",
  "sleep_hours": 7.5,
  "night_wake_times": 0,
  "difficulty_falling_asleep": "A",
  "irregular_sleep_schedule": "A",
  "exercise_minutes": 30,
  "sedentary_hours": 4,
  "fruit_veg_servings": 5,
  "fast_food_times": 0,
  "sugary_drinks": 0,
  "screen_time_hours": 3.0,
  "smoking": "A",
  "alcohol": "A",
  "late_night": "A",
  "risk_score_emotion": "A",
  "risk_score_focus": "A",
  "risk_score_body": "A"
}
```

Response includes: overall health score, risk level, 8 module results, priority focus, action plan.

### POST /api/v1/emotion/analyze — Example

```json
{
  "language": "English",
  "mood_key": "Anxious",
  "event_key": "Academic or work-related issue",
  "energy": 4,
  "stress": 8
}
```

Response includes: emotional pattern, summary, tonight/tomorrow plan, reflection guidance, breathing practice, full story.

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # pydantic-settings configuration
│   ├── database.py             # SQLAlchemy engine & session
│   ├── models/
│   │   ├── base.py             # ORM declarative base
│   │   ├── health_record.py    # HealthRecord model (42 columns)
│   │   └── emotion_record.py   # EmotionRecord model (15 columns)
│   ├── schemas/
│   │   ├── common.py           # Shared Pydantic models
│   │   ├── health.py           # Health API request/response schemas
│   │   └── emotion.py          # Emotion API request/response schemas
│   ├── api/
│   │   ├── router.py           # Central route registration
│   │   ├── health.py           # Health check API routes
│   │   └── emotion.py          # Emotion analysis API routes
│   ├── services/
│   │   ├── health_analyzer.py  # Risk scoring & interaction analysis
│   │   ├── health_check.py     # Health orchestration service
│   │   └── emotion_analysis.py # Emotion orchestration service
│   ├── engines/                # 8 health + 1 emotion engine
│   │   ├── emotion.py          # Emotion analysis engine
│   │   ├── bmi.py
│   │   ├── water_ratio.py
│   │   ├── sleep.py
│   │   ├── activity.py
│   │   ├── diet.py
│   │   ├── mental_healthy.py
│   │   ├── screen_time.py
│   │   └── habit.py
│   └── tests/                  # 84 tests across 8 test files
│       ├── test_engines.py
│       ├── test_analyzer.py
│       ├── test_health_check.py
│       ├── test_api_health.py
│       ├── test_emotion_engine.py
│       ├── test_emotion_analysis.py
│       ├── test_api_emotion.py
│       ├── test_e2e.py
│       └── conftest.py
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_create_health_records.py
│       └── 002_create_emotion_records.py
├── alembic.ini
├── pyproject.toml
├── README.md
├── CHANGELOG.md
└── scripts/
    └── check_backend.py
```

## Language Support

- `language` parameter accepts `"English"` or `"中文"`
- All diagnostic texts, risk levels, and reports are bilingual
- Korean support planned for future versions

## Development Status

Current: **Phase 1** (Backend API with 8 health assessment engines + emotion analysis)
Next: User authentication (JWT), AI report generation (OpenAI/DeepSeek), Korean language support

See [CHANGELOG.md](CHANGELOG.md) for detailed progress.
