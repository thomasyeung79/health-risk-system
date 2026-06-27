# Release Notes — v0.3 Demo

**Release Date**: 2026-06-27  
**Tag**: `v0.3-demo`  
**Previous**: `v0.2` (no tag)

---

## What's New

### Wellness OS Backend (6 new API modules)

| Module | Endpoints | Description |
|--------|-----------|-------------|
| **Members** | `POST/GET/PATCH/DELETE /api/v1/members` | Full CRUD for member profiles with multilingual support |
| **Consultations** | `POST/GET /api/v1/consultations` | Session tracking with type, concern, and questionnaire data |
| **AI Reports** | `POST /api/v1/ai-reports/generate`, `GET /api/v1/ai-reports` | Deterministic AI report generation — rule-based, no external API needed |
| **Healing Plans** | `POST/GET/PATCH /api/v1/healing-plans` | Structured wellness plans with status tracking |
| **Community Cases** | `POST/GET /api/v1/community-cases` | Anonymised case studies with public/private publishing |
| **Dashboard** | `GET /api/v1/dashboard/summary` | Aggregated KPI dashboard across all modules |

### Admin Dashboard (`pages/7_Admin.py`)

- Professional sidebar navigation with 6 sections
- KPI metric cards (members, consultations, reports, plans, cases)
- Member management with list + create form
- AI report generation by member ID
- Healing plan management with status updates
- Community case publishing with category/language filters

### Demo Data Generator (`scripts/seed_demo_data.py`)

One-command seeding script that populates the database with portfolio-quality demo data:

| Entity | Records |
|--------|---------|
| Members | 30+ (EN / 中文 / 한국어) |
| Health Records | 300 |
| Emotion Records | 140+ |
| Consultations | 80 |
| AI Reports | 60+ |
| Healing Plans | 40 |
| Community Cases | 50 |

### Under the Hood

- `modules/admin_ui.py` — Reusable admin components (metric_card, status_badge, render_table, empty_state)
- `api_client/admin_client.py` — Typed API client for all 6 Wellness OS modules
- `modules/emotion_localization.py` — Centralised emotion label mapping for multilingual support
- `modules/chart_utils.py` — Matplotlib font configuration for CJK characters
- Alembic migration `005_create_wellness_os_tables.py` — 5 new database tables

---

## Metrics

| Metric | v0.2 | v0.3 |
|--------|------|------|
| Python files | ~55 | ~80 |
| API endpoints | 14 | 25+ |
| Database tables | 6 | 11 |
| Tests | 185 | 202 |
| Alembic migrations | 4 | 5 |
| Documentation files | 4 | 6 |

---

## How to Run

```bash
# Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# Start frontend (new terminal)
streamlit run web_v1.py --server.port 8501

# Seed demo data (optional)
cd backend && python scripts/seed_demo_data.py

# Login: admin / admin123
# Navigate to "Wellness OS" in the top nav
```

---

## Known Limitations

- SQLite is used for development — migrate to PostgreSQL for production
- AI reports use a deterministic rule-based engine (OpenAI/DeepSeek adapter ready but not connected)
- No mobile-responsive frontend yet (Streamlit limitation, Next.js planned)
- Korean (한국어) member names are rendered in the UI but full Korean i18n is pending

---

## What's Next

| Item | Priority |
|------|----------|
| PostgreSQL migration | Medium |
| Recommendation engine | Low |
| Next.js frontend | Medium |
| Real AI provider integration | Low |
| Production deployment | High |
