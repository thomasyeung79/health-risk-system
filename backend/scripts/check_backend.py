"""Backend health check script.
Run: python scripts/check_backend.py
"""
import importlib
import sys
from pathlib import Path


def main():
    print()
    print("  AI Wellness Backend -- Health Check")
    print()
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  CWD:    {Path.cwd()}")
    print()

    ok = True

    # 1. Imports
    print("-- Imports ---------------------------------")
    checks = [
        ("config", "app.config"),
        ("database", "app.database"),
        ("models.base", "app.models.base"),
        ("models.health_record", "app.models.health_record"),
        ("models.emotion_record", "app.models.emotion_record"),
        ("schemas.health", "app.schemas.health"),
        ("schemas.emotion", "app.schemas.emotion"),
        ("api.health", "app.api.health"),
        ("api.emotion", "app.api.emotion"),
        ("main (FastAPI)", "app.main"),
    ]
    for name, path in checks:
        try:
            importlib.import_module(path)
            print(f"  [PASS] {name}")
        except Exception as e:
            print(f"  [FAIL] {name} -- {str(e).split(chr(10))[0]}")
            ok = False

    # 2. Database
    print()
    print("-- Database --------------------------------")
    try:
        from app.database import engine
        from sqlalchemy import inspect

        with engine.connect() as conn:
            inspector = inspect(conn)
            tables = inspector.get_table_names()
            print(f"  [PASS] SQLite connection (tables: {tables})")

            for tbl in ["health_records", "emotion_records"]:
                if tbl in tables:
                    cols = len(inspector.get_columns(tbl))
                    print(f"  [PASS] {tbl} ({cols} columns)")
                else:
                    print(f"  [FAIL] {tbl} missing")
                    ok = False
    except Exception as e:
        print(f"  [FAIL] Database -- {str(e).split(chr(10))[0]}")
        ok = False

    # 3. API checks
    print()
    print("-- API -------------------------------------")
    try:
        from app.main import app
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            # GET /health
            resp = client.get("/health")
            data = resp.json()
            if resp.status_code == 200 and data.get("status") == "ok":
                print(f"  [PASS] GET /health (HTTP {resp.status_code})")
            else:
                print(f"  [FAIL] GET /health returned {resp.status_code}: {data}")
                ok = False

            # GET /api/v1/emotion/stats
            resp = client.get("/api/v1/emotion/stats")
            if resp.status_code == 200:
                data = resp.json()
                print(f"  [PASS] GET /api/v1/emotion/stats (total_records={data['total_records']})")
            else:
                print(f"  [FAIL] GET /api/v1/emotion/stats returned {resp.status_code}")
                ok = False

            # POST /api/v1/emotion/analyze
            payload = {
                "language": "English",
                "mood_key": "Calm",
                "event_key": "Nothing special",
                "energy": 7,
                "stress": 3,
            }
            resp = client.post("/api/v1/emotion/analyze", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                has_keys = {"summary", "pattern", "breathing", "full_story"}.issubset(data.keys())
                if has_keys:
                    print(f"  [PASS] POST /api/v1/emotion/analyze (id={data['id']}, pattern={data['pattern']['pattern']})")
                else:
                    print(f"  [FAIL] POST /api/v1/emotion/analyze response missing keys: {data.keys()}")
                    ok = False
            else:
                print(f"  [FAIL] POST /api/v1/emotion/analyze returned {resp.status_code}")
                ok = False

            # GET /api/v1/health/stats
            resp = client.get("/api/v1/health/stats")
            if resp.status_code == 200:
                print(f"  [PASS] GET /api/v1/health/stats")
            else:
                print(f"  [FAIL] GET /api/v1/health/stats returned {resp.status_code}")
                ok = False

    except Exception as e:
        print(f"  [FAIL] API -- {str(e).split(chr(10))[0]}")
        ok = False

    # Summary
    print()
    print("-- Summary ---------------------------------")
    if ok:
        print("  Status: ALL CHECKS PASSED")
        print()
        print("  Start server: uvicorn app.main:app --reload --port 8000")
        print("  API docs:     http://localhost:8000/docs")
        print("  Run tests:    pytest -v")
        return 0
    else:
        print("  Status: SOME CHECKS FAILED")
        print("  Review the [FAIL] lines above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
