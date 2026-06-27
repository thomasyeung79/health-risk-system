"""AI Wellness OS — Demo Data Generator.

Populates the database with realistic sample data for portfolio demonstrations.
Idempotent: safe to run multiple times.

Usage:
    cd backend
    python scripts/seed_demo_data.py

Requires:
    - Backend running on localhost:8000
    - pip install requests
"""
import json
import random
import sys
from datetime import datetime

import requests

API = "http://localhost:8000"
MEMBER_COUNT = 30
HEALTH_RECORD_COUNT = 300
CONSULTATION_COUNT = 80
HEALING_PLAN_COUNT = 40
COMMUNITY_CASE_COUNT = 50

ENGLISH_NAMES = [
    "Alice Johnson", "Bob Williams", "Carol Davis", "Daniel Brown", "Eva Martinez",
    "Frank Wilson", "Grace Taylor", "Henry Anderson", "Ivy Thomas", "Jack Jackson",
    "Karen White", "Leo Harris", "Mia Martin", "Noah Robinson", "Olivia Clark",
    "Peter Lewis", "Quinn Walker", "Rachel Hall", "Sam Young", "Tina King",
]
CHINESE_NAMES = ["王伟", "李芳", "张磊", "刘洋", "陈静", "杨帆", "赵敏", "黄丽", "周强", "吴秀英"]
KOREAN_NAMES = ["金敏洙", "李智恩", "朴哲秀", "崔由那", "郑泰荣"]

ALL_NAMES = (ENGLISH_NAMES + CHINESE_NAMES + KOREAN_NAMES)[:MEMBER_COUNT]
random.shuffle(ALL_NAMES)

CONSULTATION_TOPICS = [
    ("initial", "Stress management and work-life balance"),
    ("follow-up", "Sleep quality improvement progress"),
    ("initial", "Anxiety and emotional regulation"),
    ("emergency", "Acute stress episode"),
    ("follow-up", "Exercise routine adaptation"),
    ("initial", "Diet and nutrition counseling"),
    ("follow-up", "Mindfulness practice review"),
    ("initial", "Career transition anxiety"),
    ("follow-up", "Relationship stress management"),
    ("initial", "Academic pressure and burnout"),
    ("initial", "Family dynamics and emotional health"),
    ("follow-up", "Breathing technique effectiveness"),
    ("initial", "Post-trauma recovery support"),
    ("follow-up", "Social anxiety coping strategies"),
    ("initial", "Grief and loss counseling"),
]
random.shuffle(CONSULTATION_TOPICS)

HEALING_PLANS = [
    ("Mindfulness Meditation", "8-week mindfulness program for stress reduction"),
    ("Better Sleep Protocol", "Evidence-based sleep hygiene improvement plan"),
    ("Daily Walking Routine", "Progressive walking program from 10 to 60 minutes"),
    ("Journaling for Clarity", "Structured reflective journaling practice"),
    ("Tai Chi for Balance", "Gentle movement practice for mind-body harmony"),
    ("Tea Meditation", "Mindful tea drinking as a daily grounding practice"),
    ("Music Therapy", "Curated playlist and active listening exercises"),
    ("Breathing Foundations", "Daily breathing practice from 2 to 15 minutes"),
    ("Gratitude Practice", "Daily three-things gratitude journaling"),
    ("Digital Detox", "Step-by-step screen time reduction plan"),
    ("Nature Connection", "Weekly outdoor time prescription"),
    ("Strength Training", "Bodyweight exercise progression program"),
    ("Social Connection", "Weekly social engagement building plan"),
    ("Creative Expression", "Art, music, or writing for emotional release"),
    ("Stress Inoculation", "Gradual exposure to manageable stressors"),
    ("Morning Routine", "Structured morning ritual design"),
    ("Evening Wind-Down", "Bedtime routine for better sleep preparation"),
    ("Nutrition Reset", "Whole-food based nutritional improvement plan"),
    ("Body Scan Practice", "Progressive body awareness meditation"),
    ("Loving-Kindness", "Metta meditation practice for self-compassion"),
]

COMMUNITY_CASES = [
    ("Anxiety recovery through mindfulness", "Anxiety", "30yo professional with GAD completed 12-week mindfulness program with 70% symptom reduction.", "MBCT + daily 20-min meditation practice", "Reduced GAD-7 score from 15 to 4 over 3 months"),
    ("Stress management success", "Stress", "45yo executive with chronic work stress learned to integrate micro-breaks and breathing.", "Structured break scheduling + box breathing", "Stress level self-report decreased from 8/10 to 4/10"),
    ("Sleep transformation journey", "Sleep", "28yo student with chronic insomnia (6 months) rebuilt sleep hygiene and circadian rhythm.", "CBT-I protocol + morning light exposure + consistent bedtime", "Sleep onset reduced from 90min to 15min; total sleep increased by 2h"),
    ("Burnout recovery story", "Burnout", "35yo teacher with severe burnout took 8-week structured recovery program.", "Complete work pause + nature therapy + gradual re-entry plan", "Returned to work part-time with sustainable boundaries"),
    ("Relationship healing", "Relationships", "42yo individual worked through relationship anxiety and attachment patterns.", "Attachment-based therapy + communication skills practice", "Reported improved relationship satisfaction and reduced conflict"),
    ("Workplace wellness win", "Work", "38yo developer with remote work isolation built social connection system.", "Co-working spaces + weekly team check-ins + hobby groups", "Loneliness score decreased 60%; productivity improved"),
    ("Study stress solution", "Study", "22yo graduate student with exam anxiety learned effective study-rest balance.", "Pomodoro technique + weekly rest day + peer study groups", "Exam scores improved 25%; anxiety during tests reduced significantly"),
    ("General wellness reboot", "General Wellness", "55yo individual with no specific diagnosis but low energy and motivation.", "Comprehensive lifestyle audit + small habit stacking", "Energy levels restored; daily step count increased from 3000 to 8000"),
]

SITUATIONS = ["A", "A", "B", "A", "C"]
CHOICES_ABC = ["A", "A", "A", "B", "C"]
CHOICES_AB = ["A", "A", "A", "A", "B"]
MOODS = ["Calm", "Calm", "Calm", "Tired", "Tired", "Anxious", "Low", "Angry", "Numb"]
EVENTS = ["Nothing special", "Nothing special", "Had a long day", "Academic or work-related issue", "Felt overwhelmed", "Felt lonely", "Argued with someone"]
COUNTRIES = ["UK", "USA", "Canada", "Australia", "Ireland", "Singapore"]

STATUSES = ["active", "active", "active", "completed", "completed", "pending"]
CATEGORIES = ["Anxiety", "Stress", "Sleep", "Burnout", "Relationships", "Work", "Study", "General Wellness"]
LANGUAGES = ["English", "English", "English", "中文", "English"]


def pick(lst):
    return random.choice(lst)


def rf(lo, hi):
    return round(random.uniform(lo, hi), 1)


def ri(lo, hi):
    return random.randint(lo, hi)


def get_token():
    r = requests.post(f"{API}/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    if r.status_code == 200:
        return r.json()["access_token"]
    requests.post(f"{API}/api/v1/auth/register", json={"username": "admin", "password": "admin123", "display_name": "Admin User"})
    r = requests.post(f"{API}/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    return r.json()["access_token"]


def seed_members(headers):
    print(f"  Members ({MEMBER_COUNT})...", end=" ", flush=True)
    members = []
    for name in ALL_NAMES:
        if name in KOREAN_NAMES:
            lang, country = "Korean", "South Korea"
        elif name in CHINESE_NAMES:
            lang, country = "中文", "China"
        else:
            lang, country = "English", pick(COUNTRIES)
        r = requests.post(f"{API}/api/v1/members", json={
            "name": name, "gender": pick(["Male", "Female"]), "age": ri(18, 75),
            "country": country, "preferred_language": lang,
        }, headers=headers)
        if r.status_code == 201:
            d = r.json()
            members.append({"id": d["id"], "name": name, "age": d["age"], "language": lang})
    print(f"{len(members)} created")
    return members


def seed_health_records(headers, members):
    print(f"  Health records ({HEALTH_RECORD_COUNT})...", end=" ", flush=True)
    count = 0
    for _ in range(HEALTH_RECORD_COUNT):
        m = pick(members)
        payload = {
            "language": m["language"],
            "weight_kg": rf(50, 100), "height_cm": ri(155, 185), "water_l": rf(1.0, 3.5),
            "situation": pick(SITUATIONS), "thirst_level": pick(CHOICES_ABC), "urine_color": pick(CHOICES_ABC),
            "sleep_hours": rf(5, 9), "night_wake_times": ri(0, 4),
            "difficulty_falling_asleep": pick(CHOICES_ABC), "irregular_sleep_schedule": pick(CHOICES_ABC),
            "exercise_minutes": ri(5, 60), "sedentary_hours": ri(4, 12),
            "fruit_veg_servings": ri(1, 6), "fast_food_times": ri(0, 4), "sugary_drinks": ri(0, 3),
            "screen_time_hours": rf(2, 10),
            "smoking": pick(CHOICES_AB), "alcohol": pick(CHOICES_AB), "late_night": pick(CHOICES_ABC),
            "risk_score_emotion": pick(CHOICES_ABC), "risk_score_focus": pick(CHOICES_ABC), "risk_score_body": pick(CHOICES_ABC),
        }
        r = requests.post(f"{API}/api/v1/health/check", json=payload, headers=headers)
        if r.status_code == 200:
            count += 1
    print(f"{count} created")


def seed_emotion_records(headers, members):
    print(f"  Emotion records...", end=" ", flush=True)
    count = 0
    for m in members:
        for _ in range(ri(2, 8)):
            r = requests.post(f"{API}/api/v1/emotion/analyze", json={
                "language": m["language"], "mood_key": pick(MOODS), "event_key": pick(EVENTS),
                "energy": ri(2, 9), "stress": ri(2, 9),
            }, headers=headers)
            if r.status_code == 200:
                count += 1
    print(f"{count} created")


def seed_consultations(headers, members):
    print(f"  Consultations ({CONSULTATION_COUNT})...", end=" ", flush=True)
    consults = []
    for i in range(CONSULTATION_COUNT):
        m = pick(members)
        t = CONSULTATION_TOPICS[i % len(CONSULTATION_TOPICS)]
        r = requests.post(f"{API}/api/v1/consultations", json={
            "member_id": m["id"], "consultation_type": t[0], "main_concern": t[1],
        }, headers=headers)
        if r.status_code == 201:
            consults.append({"id": r.json()["id"], "member_id": m["id"]})
    print(f"{len(consults)} created")
    return consults


def seed_ai_reports(headers, consultations, members):
    print(f"  AI reports...", end=" ", flush=True)
    count = 0
    for c in consultations[:60]:
        r = requests.post(f"{API}/api/v1/ai-reports/generate", json={
            "member_id": c["member_id"], "consultation_id": c["id"],
        }, headers=headers)
        if r.status_code == 201:
            count += 1
    consulted = {c["member_id"] for c in consultations}
    for m in members:
        if m["id"] not in consulted:
            r = requests.post(f"{API}/api/v1/ai-reports/generate", json={"member_id": m["id"]}, headers=headers)
            if r.status_code == 201:
                count += 1
    print(f"{count} created")


def seed_healing_plans(headers, members):
    print(f"  Healing plans ({HEALING_PLAN_COUNT})...", end=" ", flush=True)
    count = 0
    for i in range(HEALING_PLAN_COUNT):
        m = pick(members)
        title, desc = HEALING_PLANS[i % len(HEALING_PLANS)]
        r = requests.post(f"{API}/api/v1/healing-plans", json={
            "member_id": m["id"], "title": title, "description": desc,
            "plan_items": json.dumps([{"week": w, "task": f"{title[:20]} — Week {w}"} for w in range(1, 9)]),
            "status": pick(STATUSES),
        }, headers=headers)
        if r.status_code == 201:
            count += 1
    print(f"{count} created")


def seed_community_cases(headers):
    print(f"  Community cases ({COMMUNITY_CASE_COUNT})...", end=" ", flush=True)
    count = 0
    for i in range(COMMUNITY_CASE_COUNT):
        t, cat, summary, approach, outcome = COMMUNITY_CASES[i % len(COMMUNITY_CASES)]
        r = requests.post(f"{API}/api/v1/community-cases", json={
            "title": t, "category": cat, "anonymized_summary": summary,
            "healing_approach": approach, "outcome": outcome,
            "language": pick(LANGUAGES), "is_public": True,
        }, headers=headers)
        if r.status_code == 201:
            count += 1
    print(f"{count} created")


def verify(headers):
    print(f"\n  {'='*50}")
    r = requests.get(f"{API}/api/v1/dashboard/summary", headers=headers)
    if r.status_code == 200:
        d = r.json()
        print(f"  Dashboard: {d['total_members']} members, {d['total_consultations']} consults, {d['total_ai_reports']} reports, {d['total_healing_plans']} plans, {d['total_community_cases']} cases")
    else:
        print(f"  Dashboard: ERROR {r.status_code}")
    r = requests.get(f"{API}/api/v1/members?limit=3", headers=headers)
    if r.status_code == 200:
        for m in r.json().get("items", []):
            print(f"    Member: {m['name']} ({m['age']}, {m['country']})")


def main():
    print()
    print("  AI Wellness OS — Demo Data Generator")
    print()
    print(f"  API: {API}")

    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  Auth: OK ({token[:15]}...)")
    print()

    members = seed_members(headers)
    if not members:
        print("  ERROR: No members created. Exiting.")
        sys.exit(1)

    seed_health_records(headers, members)
    seed_emotion_records(headers, members)
    consultations = seed_consultations(headers, members)
    seed_ai_reports(headers, consultations, members)
    seed_healing_plans(headers, members)
    seed_community_cases(headers)

    print()
    verify(headers)
    print()
    print(f"  Done! Login at http://localhost:8501")
    print(f"  Username: admin  Password: admin123")
    print()


if __name__ == "__main__":
    main()
