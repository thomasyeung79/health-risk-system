# Changelog

All notable changes to AI Wellness Platform are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses semantic versioning for portfolio releases.

## [0.4.0] — 2026-06-29 — AI Provider + Growth Journey

### Added
- **AI Provider System**: Pluggable provider layer with abstract interface
  - `RuleBasedProvider` — deterministic default fallback (preserves existing behavior)
  - `OpenAIProvider` — placeholder for future OpenAI integration
  - `DeepSeekProvider` — placeholder for future DeepSeek integration
  - Provider selection via `AI_PROVIDER=rule_based|openai|deepseek` env var
  - Safe fallback to rule_based when API key is missing
  - Factory function `create_ai_provider()` in `app/services/ai_providers.py`
- **Growth Journey Module**: Timeline-style personal wellness growth story
  - New `growth_journeys` database table (id, member_id, title, summary, timeline_items, insights)
  - Rule-based generation combining health records, emotion records, consultations, AI reports, and healing plans
  - Timeline events, emotional patterns, key challenges, healing actions, progress summary, next-step suggestions
  - 3 new API endpoints: POST `/growth-journeys/generate`, GET `/growth-journeys` (filterable by member_id), GET `/growth-journeys/{id}`
  - Administration Dashboard section with member input, generation, timeline view, insights, and next steps
- **25 new tests** covering:
  - AI provider factory fallback (env var absent, missing key, unknown provider)
  - RuleBasedProvider content generation (EN/CN, risk levels, age defaults)
  - OpenAI/DeepSeek placeholder providers
  - Growth Journey generation, list, detail, user isolation

### Changed
- Refactored `ai_report_service.py` to use the pluggable `AIProvider` interface
- Router registration expanded from 11 to 12 route modules (added growth_journeys)
- Administration dashboard now includes "Growth Journey" in sidebar navigation
- Updated README with v0.4 features, revised API table, and roadmap

### Preserved
- All existing tests remain unchanged
- No breaking changes to existing APIs
- Rule-based provider produces identical output to previous hardcoded logic

## [0.5.0] — 2026-07-01 — Product Intelligence Upgrade

### Added
- **Pattern Discovery Engine** — automatically discovers behaviour patterns from health and emotion records (sleep→stress, exercise→energy, health trajectory, emotional stability, diet→energy). Confidence scoring, evidence summaries, recommendations. API: `GET /api/v1/patterns/{member_id}`
- **Insights Dashboard** — Today's Wellness Score, Monthly Trend, Positive Changes, Risk Alerts, Recommended Focus, Recent Achievements. Meaningful narrative summaries instead of raw numbers. API: `GET /api/v1/insights/{member_id}`
- **AI Coach** — generates one daily coaching message per member (not a chatbot). Includes today's focus, habit suggestion, motivation, wellness reminder. Seeded RNG for deterministic daily output. API: `GET /api/v1/coach/daily/{member_id}`
- **Daily Reflection** — new `daily_reflections` table with went_well, biggest_challenge, gratitude, notes fields. Weekly summary generation with keyword theme extraction. APIs: `POST /api/v1/reflections`, `GET /api/v1/reflections`, `GET /api/v1/reflections/weekly-summary/{member_id}`
- **Wellness Timeline upgrade** — Growth Journey now includes reflection events, narrative milestones between event type transitions, richer story-like descriptions, and improved bilingual flow
- **21 new tests** covering all 5 modules: pattern discovery (empty, with data, 404, auth), insights (empty, with data, 404, auth), coach (daily message, determinism, 404, auth), reflections (create/list/summary, 404, auth)

### Changed
- Router registration expanded from 12 to 16 route modules (patterns, insights, coach, reflections)
- Administration Dashboard sidebar now includes "Insights" page with 4 tabs (Insights, Patterns, Coach, Reflections)
- Growth Journey service upgraded to include reflections and narrative milestones
- API client extended with 6 new methods for pattern discovery, insights, coach, and reflections

### Preserved
- All 231 existing tests unchanged
- No breaking changes to existing APIs
- All rule-based — no external API calls during tests

## [1.0.0-rc.3] - 2026-06-21

### Fixed
- Removed duplicate `render_medical_disclaimer()` definition that was overwriting the DISCLAIMER-backed version.
- Added `get_disclaimer_text()` pure function and `render_medical_disclaimer()` for consistent bilingual disclaimer rendering.

### Changed
- Bumped version from rc.1 to rc.3 to align all version references (README badge, backend, footer).
- database.py: made file paths absolute to fix Docker/PyInstaller working-directory issues.
- Wellness History page: added record deduplication when both API and local data sources have overlapping records.

## [1.0.0-rc.1] - 2026-06-18

### Added
- API-first FastAPI backend with Streamlit frontend integration.
- JWT authentication with refresh token rotation and user isolation.
- Eight-module health assessment covering BMI, activity, sleep, diet, hydration, screen time, habits, and mental wellness.
- Emotion analysis workflow with persistent records and dashboard insights.
- AI wellness report generation with deterministic local fallback when provider keys are unavailable.
- Trend summary endpoints for health and emotion records.
- Docker Compose deployment path with frontend, backend, and nginx configuration.
- Alembic migrations for health records, emotion records, report records, users, and refresh tokens.
- Backend CI workflow and pytest coverage across engines, services, API routes, auth, user isolation, and E2E flows.

### Security
- Added bcrypt password hashing, JWT access tokens, refresh token persistence, and logout revocation.
- Added database-layer user filtering and tests to prevent cross-user data access.

### Documentation
- Added deployment guide, architecture documentation, API overview, screenshots, and setup instructions.

### Notes
- This is a portfolio release candidate. It is not medical advice and should be used with sample data only.
