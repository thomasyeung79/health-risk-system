# Changelog

All notable changes to AI Wellness Platform are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses semantic versioning for portfolio releases.

## [0.3.0] — 2026-06-27 — AI Wellness OS

### Added
- **Wellness OS backend**: 6 new API modules with 11+ new endpoints
- **Admin Dashboard**: Professional sidebar navigation with KPI metric cards
- **Member Management**: Full CRUD for wellness members with multilingual profiles (EN / Chinese / Korean)
- **Consultation Management**: Session tracking with type, concern, and questionnaire data
- **AI Report Generation**: Deterministic rule-based reports per member (OpenAI/DeepSeek ready)
- **Healing Plans**: Structured wellness plans with progress status tracking
- **Community Cases**: Anonymised case studies with public/private publishing
- **Demo Data Generator**: One-command seeding with 30+ members, 300 health records, 80 consultations, 60 AI reports, 40 healing plans, 50 community cases
- **Reusable admin UI components** (`modules/admin_ui.py`)
- **Admin API client** (`api_client/admin_client.py`)
- **Emotion localization module** for multilingual label support
- **Chart utilities** for CJK font rendering
- **Alembic migration 005** with 5 new database tables
- **17 new tests** covering all Wellness OS endpoints
- **CONTRIBUTING.md** and **RELEASE_NOTES_v0.3.md**

### Changed
- Updated README with Mermaid architecture diagram and Wellness OS branding
- Router registration expanded from 6 to 11 route modules
- Enhanced datetime parsing robustness in trend charts

### Preserved
- All 185 existing tests remain unchanged
- No breaking changes to existing APIs

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
