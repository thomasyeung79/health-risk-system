"""Health check orchestration service.

Calls all 8 engines, aggregates results, computes overall analysis,
and persists the record to the database.
"""
from typing import Any

from sqlalchemy.orm import Session

from app.engines.bmi import calc_bmi
from app.engines.water_ratio import calc_water_ratio
from app.engines.sleep import calc_sleep
from app.engines.activity import calc_activity
from app.engines.diet import calc_diet
from app.engines.mental_healthy import calc_mental_healthy
from app.engines.screen_time import calc_screen_time
from app.engines.habit import calc_habit
from app.models.health_record import HealthRecord
from app.services.health_analyzer import calculate_overall_result


def run_health_check(
    db: Session,
    language: str,
    *,
    weight_kg: float,
    height_cm: float,
    water_l: float,
    situation: str,
    thirst_level: str,
    urine_color: str,
    sleep_hours: float,
    night_wake_times: int,
    difficulty_falling_asleep: str,
    irregular_sleep_schedule: str,
    exercise_minutes: int,
    sedentary_hours: int,
    fruit_veg_servings: int,
    fast_food_times: int,
    sugary_drinks: int,
    screen_time_hours: float,
    smoking: str,
    alcohol: str,
    late_night: str,
    risk_score_emotion: str,
    risk_score_focus: str,
    risk_score_body: str,
) -> dict[str, Any]:
    """Run the full health check and persist results."""

    # Run all 8 engines
    bmi_result = calc_bmi(weight_kg, height_cm, language)
    water_result = calc_water_ratio(water_l, situation, weight_kg, thirst_level, urine_color, language)
    sleep_result = calc_sleep(sleep_hours, night_wake_times, difficulty_falling_asleep, irregular_sleep_schedule, language)
    activity_result = calc_activity(exercise_minutes, sedentary_hours, language)
    diet_result = calc_diet(fruit_veg_servings, fast_food_times, sugary_drinks, language)
    mental_result = calc_mental_healthy(risk_score_emotion, risk_score_focus, risk_score_body, language)
    screen_result = calc_screen_time(screen_time_hours, language)
    habit_result = calc_habit(smoking, alcohol, late_night, language)

    results = [
        bmi_result, water_result, sleep_result, activity_result,
        diet_result, mental_result, screen_result, habit_result,
    ]

    # Compute overall analysis
    overall = calculate_overall_result(results, language)

    # Persist to database
    record = HealthRecord(
        language=language,
        weight_kg=weight_kg,
        height_cm=height_cm,
        water_l=water_l,
        situation=situation,
        thirst_level=thirst_level,
        urine_color=urine_color,
        sleep_hours=sleep_hours,
        night_wake_times=night_wake_times,
        difficulty_falling_asleep=difficulty_falling_asleep,
        irregular_sleep_schedule=irregular_sleep_schedule,
        exercise_minutes=exercise_minutes,
        sedentary_hours=sedentary_hours,
        fruit_veg_servings=fruit_veg_servings,
        fast_food_times=fast_food_times,
        sugary_drinks=sugary_drinks,
        screen_time_hours=screen_time_hours,
        smoking=smoking,
        alcohol=alcohol,
        late_night=late_night,
        risk_score_emotion=risk_score_emotion,
        risk_score_focus=risk_score_focus,
        risk_score_body=risk_score_body,
        bmi_score=bmi_result["score"],
        water_score=water_result["score"],
        sleep_score=sleep_result["score"],
        activity_score=activity_result["score"],
        diet_score=diet_result["score"],
        mental_score=mental_result["score"],
        screen_score=screen_result["score"],
        habit_score=habit_result["score"],
        health_score=overall["health_score"],
        risk_percent=overall["risk_percent"],
        risk_level=overall["risk_level"],
        risk_score=overall["risk_score"],
        max_risk_score=overall["max_risk_score"],
        interaction_score=overall["interaction_score"],
        overall=overall["overall"],
        primary_focus=overall["primary_focus"],
        action_plan="|".join(overall["action_plan"]),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Build response
    return {
        "id": record.id,
        "created_at": record.created_at.isoformat(),
        "language": language,
        "health_score": overall["health_score"],
        "risk_percent": overall["risk_percent"],
        "risk_level": overall["risk_level"],
        "modules": {
            r["name"]: {
                "score": r["score"],
                "level": r["level"],
                "reasons": r["reasons"],
                "suggestions": r["suggestions"],
            }
            for r in results
        },
        "overall": overall["overall"],
        "primary_focus": overall["primary_focus"],
        "action_plan": overall["action_plan"],
    }
