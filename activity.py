def calc_activity(exercise_minutes, sedentary_hours):
   activity_score = 0
   reasons_activity = []
   suggestions_activity = []
   #exercise
   if exercise_minutes >= 30:
     activity_score += 0
   elif 10 <= exercise_minutes < 30:
     activity_score += 1
     reasons_activity.append("Physical activity is below the recommended level.")
     suggestions_activity.append("Increase daily activity time to at least 30 minutes of moderate exercise.")
   else:
     activity_score += 2
     reasons_activity.append("Very little physical activity has been recorded today. ")
     suggestions_activity.append("Try to include at least 20–30 minutes of light exercise such as walking or stretching.")
   #sedentary
   if sedentary_hours >= 10:
     activity_score += 2
     reasons_activity.append("Prolonged sedentary time has been recorded today.")
     suggestions_activity.append("Reduce sitting time and stand or walk for a few minutes every hour.")
   elif 8 <= sedentary_hours < 10:
     activity_score += 1
     reasons_activity.append("Sedentary time is relatively high.")
     suggestions_activity.append("Try to take short movement breaks during long sitting periods.")
   else:
     activity_score += 0

   #cap
   if activity_score >= 4:
     risk_score_activity = 3
     level_activity = "High Risk"
   elif activity_score >= 2:
     risk_score_activity = 2
     level_activity = "Medium Risk"
   elif activity_score >= 1:
     risk_score_activity = 1
     level_activity = "Low Risk"
   else:
     risk_score_activity = 0
     level_activity = "Healthy"

   max_risk_score_activity = 3

   return {
       "name": "Activity",
       "metric_value": activity_score,
       "score": risk_score_activity,
       "level": level_activity,
       "max_score": max_risk_score_activity,
       "reasons": reasons_activity,
       "suggestions": suggestions_activity,
   }