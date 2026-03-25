def calc_diet(fruit_veg_servings, fast_food_times, sugary_drinks):
   diet_score = 0
   reasons_diet = []
   suggestions_diet = []
   #fruit_veg_servings
   if fruit_veg_servings >= 5:
       diet_score += 0
   elif 3 <= fruit_veg_servings < 5:
       diet_score += 1
       reasons_diet.append("Fruit and vegetable intake is slightly below the recommended level.")
       suggestions_diet.append("Try to include more fruits and vegetables in your daily meals.")
   else:
       diet_score += 2
       reasons_diet.append("Fruit and vegetable intake is significantly below the recommended level.")
       suggestions_diet.append("Increase daily fruit and vegetable intake to at least 5 servings.")
   #fast_food_times
   if fast_food_times >= 2:
       diet_score += 1
       reasons_diet.append("Fast food consumption is relatively high.")
       suggestions_diet.append("Reduce fast food meals and choose healthier home-cooked options.")
   else:
       diet_score += 0
   #sugary_drinks
   if sugary_drinks > 1:
       diet_score += 1
       reasons_diet.append("Sugary drink intake is above the recommended level.")
       suggestions_diet.append("Limit sugary drinks and replace them with water or low-sugar alternatives.")
   else:
       diet_score += 0

    # cap
   if diet_score >= 4:
       risk_score_diet = 3
       level_diet = "High Risk"
   elif diet_score >= 2:
       risk_score_diet = 2
       level_diet = "Medium Risk"
   elif diet_score >= 1:
       risk_score_diet = 1
       level_diet = "Low Risk"
   else:
       risk_score_diet = 0
       level_diet = "Healthy"

   max_risk_score_diet = 4
   return {
       "name": "Diet",
       "metric_value": diet_score,
       "score": risk_score_diet,
       "level": level_diet,
       "max_score": max_risk_score_diet,
       "reasons": reasons_diet,
       "suggestions": suggestions_diet,
   }