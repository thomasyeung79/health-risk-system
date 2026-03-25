def calc_bmi(weight_kg, height_cm):
   bmi = round(weight_kg / (height_cm / 100) ** 2, 1)    # World Health Organization (2000)
   reasons_bmi = []
   suggestions_bmi = []

   if bmi >= 30:                                 #超重
     risk_score_bmi = 3
     level_bmi = "High Risk"
     reasons_bmi.append("BMI is in the obesity range.")
     suggestions_bmi.append("BMI indicates obesity. Professional medical evaluation is recommended.")
   elif bmi < 18.5:                          #偏瘦
     risk_score_bmi = 2
     level_bmi = "Medium Risk"
     reasons_bmi.append("BMI outside the healthy range.")
     suggestions_bmi.append("BMI is below the healthy range. Nutritional improvement and strength training are advised.")
   elif 25 <= bmi <30:                                       #偏重
     risk_score_bmi = 1
     level_bmi = "Low Risk"
     reasons_bmi.append("BMI outside the healthy range.")
     suggestions_bmi.append("BMI is in the overweight range. Lifestyle modification is recommended.")
   elif 18.5 <= bmi < 25:
     risk_score_bmi = 0
     level_bmi = "Healthy"

   max_risk_score_bmi = 3
   return {
       "name": "BMI",
       "metric_value": bmi,
       "score": risk_score_bmi,
       "level": level_bmi,
       "max_score": max_risk_score_bmi,
       "reasons": reasons_bmi,
       "suggestions": suggestions_bmi,
   }

#European Food Safety Authority. (2010).