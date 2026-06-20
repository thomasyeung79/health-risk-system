import json
import os

import pandas as pd

# ── File paths ──────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEALTH_CSV = os.path.join(BASE_DIR, "health_records.csv")
HEALTH_JSON = os.path.join(BASE_DIR, "health_history.json")
MIND_JSON = os.path.join(BASE_DIR, "insight_records.json")
USERS_FILE = os.path.join(BASE_DIR, "wellnest_users.json")


# ── Generic helpers ─────────────────────────────────
def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_json(path, records):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def filter_user(records, username):
    return [
        r for r in records
        if r.get("user_name") == username or r.get("username") == username
    ]


# ── Health records (CSV) ────────────────────────────
def save_health_record(record):
    df_new = pd.DataFrame([record])
    if os.path.exists(HEALTH_CSV):
        df_old = pd.read_csv(HEALTH_CSV)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(HEALTH_CSV, index=False)
    return True


def load_health_records():
    if os.path.exists(HEALTH_CSV):
        return pd.read_csv(HEALTH_CSV)
    return pd.DataFrame()


# ── Health records (JSON) ───────────────────────────
def save_health_json(record):
    records = load_json(HEALTH_JSON)
    records.append(record)
    save_json(HEALTH_JSON, records)
    return True


def load_health_json():
    return load_json(HEALTH_JSON)


# ── Mind records (JSON) ─────────────────────────────
def save_mind_record(record):
    records = load_json(MIND_JSON)
    records.append(record)
    save_json(MIND_JSON, records)
    return True


def load_mind_records():
    records = load_json(MIND_JSON)
    return pd.DataFrame(records) if records else pd.DataFrame()
