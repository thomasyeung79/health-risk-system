# Contributing to AI Wellness OS

Thank you for considering contributing! This is a portfolio project, and contributions that improve code quality, documentation, or feature completeness are welcome.

## Getting Started

1. Fork the repository.
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/health-risk-system.git
   ```
3. Set up the development environment:
   ```bash
   cd AI_Wellness_Platform/backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e ".[dev]"
   cd ..
   pip install -r requirements.txt
   ```
4. Create a branch for your work:
   ```bash
   git checkout -b feat/your-feature-name
   ```

## Development Guidelines

### Backend (FastAPI)

- Add new route modules under `backend/app/api/`
- Add corresponding Pydantic schemas under `backend/app/schemas/`
- Add ORM models under `backend/app/models/`
- Add business logic under `backend/app/services/`
- Create an Alembic migration for new tables
- Register new routers in `backend/app/api/router.py`
- Import new models in `backend/alembic/env.py`

### Frontend (Streamlit)

- Add new page files under `pages/`
- Add reusable UI components under `modules/`
- Add API client methods under `api_client/`
- Register new pages in `modules/ui.py` (NAV_ITEMS)

### Testing

All new backend code must include tests:

```bash
cd backend
pytest -v app/tests/
```

Test conventions:
- Unit tests for engine/service logic
- Integration tests for API endpoints using `TestClient`
- Use `db_session` fixture for database operations
- Use `auth_headers` fixture for authenticated requests

### Code Style

- Python: Follow PEP 8
- Imports: Standard lib → third-party → local
- Type hints: Required for all function signatures
- Docstrings: Required for public functions
- Translations: Use TEXT dictionaries (English + Chinese)

## Commit Convention

```
type: short description

- Bullet point changes
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

## Pull Request Process

1. Ensure all tests pass: `cd backend && pytest -q`
2. Update documentation if adding new features
3. Create a pull request with a clear description

## Code of Conduct

Be respectful, constructive, and professional.
