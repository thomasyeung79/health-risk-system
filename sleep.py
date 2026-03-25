def calc_sleep(sleep_hours, night_wake_times):
   #sleep hours
   sleep_score = 0
   reasons_sleep = []
   suggestions_sleep = []
   if sleep_hours < 2:
     sleep_score += 3
     reasons_sleep.append('Extremely short sleep duration.')
     suggestions_sleep.append('Seek immediate rest and avoid high-risk activities. Consult a healthcare professional if this continues.')
   elif 2 <= sleep_hours < 5:
     sleep_score += 2
     reasons_sleep.append('Insufficient sleep duration.')
     suggestions_sleep.append('Aim for at least 7 hours of sleep tonight and reduce late-night screen exposure.')
   elif 5<= sleep_hours < 6:
     sleep_score += 1
     reasons_sleep.append('Borderline short sleep duration.')
     suggestions_sleep.append('Adjust bedtime slightly earlier and maintain a consistent sleep schedule.')
   elif 6 <= sleep_hours <= 8:
     sleep_score += 0
   else:
     sleep_score += 1
     reasons_sleep.append('Extended sleep duration.')
     suggestions_sleep.append('Monitor for persistent fatigue and maintain a balanced sleep routine.')

   #night wake times
   if night_wake_times >= 5:
     sleep_score += 2
     reasons_sleep.append('Very frequent night awakenings.')
     suggestions_sleep.append('Reduce fluid intake before bed and consider relaxation techniques.')
   elif 3 <= night_wake_times < 5:
     sleep_score += 1
     reasons_sleep.append('Frequent night awakenings.')
     suggestions_sleep.append('Create a quiet sleep environment and manage evening stress levels.')
   else:
     sleep_score += 0

   #cap
   if sleep_score >= 5:
     risk_score_sleep = 3
     level_sleep = "High Risk"
   elif sleep_score >= 3:
     risk_score_sleep = 2
     level_sleep = "Medium Risk"
   elif sleep_score >= 1:
     risk_score_sleep = 1
     level_sleep = "Low Risk"
   elif sleep_score == 0:
     risk_score_sleep = 0
     level_sleep = "Healthy"

   max_risk_score_sleep = 3

   return {
       "name": "Sleep",
       "metric_value": sleep_score,
       "score": risk_score_sleep,
       "level": level_sleep,
       "max_score": max_risk_score_sleep,
       "reasons": reasons_sleep,
       "suggestions": suggestions_sleep,
   }