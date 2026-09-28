# Copyright 2026 Google LLC
# External API tools for recipe-concierge agent

import os
import urllib.request
import json
from typing import List, Dict, Any

def search_public_recipes(query: str) -> List[Dict[str, Any]]:
    """Search for global online recipes using TheMealDB free public API.

    Args:
        query: The meal or recipe name to search for (e.g., 'Arrabiata', 'Tacos', 'Curry', 'Chicken').

    Returns:
        A list of matching recipe results with title, category, cuisine, thumbnail image, instructions, and ingredients.
    """
    api_key = os.environ.get("THEMEALDB_API_KEY", "1")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={encoded_query}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RecipeConcierge/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                return [{"error": f"HTTP Error {response.status}"}]
            data = json.loads(response.read().decode("utf-8"))
            
        meals = data.get("meals")
        if not meals:
            return []
            
        results = []
        for meal in meals[:3]:  # Limit to top 3 results for concise responses
            ingredients = []
            for i in range(1, 21):
                ing = meal.get(f"strIngredient{i}")
                meas = meal.get(f"strMeasure{i}")
                if ing and ing.strip():
                    measure_str = meas.strip() if meas else ""
                    ingredients.append(f"{measure_str} {ing.strip()}".strip())
                    
            results.append({
                "id": meal.get("idMeal"),
                "title": meal.get("strMeal"),
                "category": meal.get("strCategory"),
                "cuisine": meal.get("strArea"),
                "instructions": meal.get("strInstructions"),
                "thumbnail_url": meal.get("strMealThumb"),
                "youtube_url": meal.get("strYoutube"),
                "ingredients": ingredients,
            })
        return results
    except Exception as e:
        return [{"error": f"Failed to fetch public recipes: {str(e)}"}]
