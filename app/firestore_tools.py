# Copyright 2026 Google LLC
# Firestore tools for recipe-concierge agent

from typing import List, Optional, Dict, Any
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-02-4d1e13b696da"

def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with hardcoded project ID."""
    return firestore.Client(
        project=PROJECT_ID,
        client_options={"quota_project_id": PROJECT_ID}
    )

def list_recipes(cuisine: Optional[str] = None) -> List[Dict[str, Any]]:
    """List recipes stored in the Firestore database.

    Args:
        cuisine: Optional cuisine or filter category (e.g. 'Italian', 'Mediterranean').

    Returns:
        A list of recipe documents from Firestore.
    """
    db = get_firestore_client()
    recipes_ref = db.collection("recipes")
    docs = recipes_ref.stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        if cuisine and cuisine.lower() not in data.get("cuisine", "").lower():
            continue
        results.append(data)
    return results

def list_pantry_items() -> List[Dict[str, Any]]:
    """List all items currently in the user's pantry.

    Returns:
        A list of pantry item documents with name, category, quantity, and unit.
    """
    db = get_firestore_client()
    pantry_ref = db.collection("pantry")
    docs = pantry_ref.stream()
    return [doc.to_dict() for doc in docs]

def search_recipes(query: str) -> List[Dict[str, Any]]:
    """Search for recipes by ingredient, title, or keyword.

    Args:
        query: The search term (e.g., 'pasta', 'avocado', 'healthy').

    Returns:
        A list of matching recipe documents.
    """
    db = get_firestore_client()
    recipes_ref = db.collection("recipes")
    docs = recipes_ref.stream()
    
    query_lower = query.lower()
    results = []
    for doc in docs:
        data = doc.to_dict()
        title = data.get("title", "").lower()
        cuisine = data.get("cuisine", "").lower()
        ingredients = [i.lower() for i in data.get("ingredients", [])]
        tags = [t.lower() for t in data.get("tags", [])]
        
        if (query_lower in title or 
            query_lower in cuisine or 
            any(query_lower in ing for ing in ingredients) or
            any(query_lower in tag for tag in tags)):
            results.append(data)
            
    return results

def add_pantry_item(name: str, category: str, quantity: float, unit: str) -> Dict[str, Any]:
    """Add a new item or update quantity of an existing item in the pantry.

    Args:
        name: Name of the item (e.g., 'Eggs', 'Milk').
        category: Category of the item (e.g., 'Dairy', 'Produce', 'Pantry').
        quantity: Amount/number of units.
        unit: Measurement unit (e.g., 'pieces', 'loaves', 'cloves', 'carton').

    Returns:
        The created or updated pantry document data.
    """
    db = get_firestore_client()
    item_id = f"item_{name.lower().replace(' ', '_')}"
    item_data = {
        "id": item_id,
        "name": name,
        "category": category,
        "quantity": quantity,
        "unit": unit
    }
    db.collection("pantry").document(item_id).set(item_data)
    return {"status": "success", "item": item_data}

def add_recipe(title: str, cuisine: str, prep_time_minutes: int, ingredients: List[str], instructions: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Add a new recipe to the Firestore database.

    Args:
        title: Title of the recipe.
        cuisine: Cuisine category.
        prep_time_minutes: Preparation time in minutes.
        ingredients: List of ingredient strings.
        instructions: Cooking instructions.
        tags: Optional list of tag keywords.

    Returns:
        The created recipe document data.
    """
    db = get_firestore_client()
    recipe_id = f"recipe_{title.lower().replace(' ', '_')}"
    recipe_data = {
        "id": recipe_id,
        "title": title,
        "cuisine": cuisine,
        "prep_time_minutes": prep_time_minutes,
        "ingredients": ingredients,
        "instructions": instructions,
        "tags": tags or []
    }
    db.collection("recipes").document(recipe_id).set(recipe_data)
    return {"status": "success", "recipe": recipe_data}

def check_pantry_recipe_match(recipe_id: str) -> Dict[str, Any]:
    """Check if the user has required ingredients in their pantry for a specific recipe.

    Args:
        recipe_id: The ID of the recipe (e.g., 'recipe_1', 'recipe_2').

    Returns:
        A dictionary containing recipe title, matching ingredients, missing ingredients, and can_cook_now status.
    """
    db = get_firestore_client()
    recipe_doc = db.collection("recipes").document(recipe_id).get()
    
    if not recipe_doc.exists:
        return {"status": "error", "message": f"Recipe '{recipe_id}' not found."}
        
    recipe = recipe_doc.to_dict()
    recipe_ingredients = recipe.get("ingredients", [])
    
    pantry_docs = db.collection("pantry").stream()
    pantry_names = [p.to_dict().get("name", "").lower() for p in pantry_docs]
    
    matching = []
    missing = []
    
    for ing in recipe_ingredients:
        ing_lower = ing.lower()
        if any(p_name in ing_lower or ing_lower in p_name for p_name in pantry_names if p_name):
            matching.append(ing)
        else:
            missing.append(ing)
            
    return {
        "recipe_id": recipe_id,
        "title": recipe.get("title"),
        "matching_ingredients": matching,
        "missing_ingredients": missing,
        "can_cook_now": len(missing) == 0
    }

