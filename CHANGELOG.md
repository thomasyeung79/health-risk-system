# Changelog

All notable changes to AI Wellness Platform are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses semantic versioning for portfolio releases.

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
