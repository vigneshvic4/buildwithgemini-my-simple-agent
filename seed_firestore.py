# Copyright 2026 Google LLC
# Seed script for Firestore database

import time
from google.cloud import firestore
from google.api_core import exceptions

PROJECT_ID = "qwiklabs-gcp-02-4d1e13b696da"

def set_doc_with_retry(doc_ref, data, max_retries=5):
    for attempt in range(max_retries):
        try:
            doc_ref.set(data)
            return
        except exceptions.PermissionDenied:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)

def seed_database():
    db = firestore.Client(
        project=PROJECT_ID,
        client_options={"quota_project_id": PROJECT_ID}
    )
    print(f"Connecting to Firestore for project: {PROJECT_ID}")

    # Seed recipes collection
    recipes = [
        {
            "id": "recipe_1",
            "title": "Avocado & Tomato Toast",
            "cuisine": "Breakfast / Healthy",
            "prep_time_minutes": 10,
            "ingredients": ["2 slices sourdough bread", "1 ripe avocado", "1 tomato sliced", "Olive oil", "Salt and pepper"],
            "instructions": "Toast sourdough slices. Mash avocado with salt and pepper. Spread on toast and top with tomato slices and drizzle olive oil.",
            "tags": ["quick", "vegetarian", "healthy"]
        },
        {
            "id": "recipe_2",
            "title": "Garlic Butter Pasta",
            "cuisine": "Italian",
            "prep_time_minutes": 15,
            "ingredients": ["200g pasta", "4 cloves garlic minced", "3 tbsp butter", "Grated Parmesan", "Fresh parsley"],
            "instructions": "Boil pasta until al dente. In a skillet, melt butter and sauté garlic until fragrant. Toss pasta in garlic butter and top with Parmesan and parsley.",
            "tags": ["quick", "dinner", "comfort food"]
        },
        {
            "id": "recipe_3",
            "title": "Mediterranean Quinoa Bowl",
            "cuisine": "Mediterranean",
            "prep_time_minutes": 20,
            "ingredients": ["1 cup cooked quinoa", "1/2 cup cucumber diced", "1/2 cup cherry tomatoes halved", "1/4 cup feta cheese", "Kalamata olives", "Lemon vinaigrette"],
            "instructions": "Combine quinoa, cucumber, tomatoes, olives, and feta in a bowl. Drizzle with lemon vinaigrette and toss gently.",
            "tags": ["healthy", "lunch", "gluten-free"]
        }
    ]

    print("Seeding recipes...")
    for recipe in recipes:
        doc_ref = db.collection("recipes").document(recipe["id"])
        set_doc_with_retry(doc_ref, recipe)
        print(f"  Added recipe: {recipe['title']} ({recipe['id']})")

    # Seed pantry collection
    pantry_items = [
        {
            "id": "item_1",
            "name": "Avocado",
            "category": "Produce",
            "quantity": 3,
            "unit": "pieces"
        },
        {
            "id": "item_2",
            "name": "Sourdough Bread",
            "category": "Bakery",
            "quantity": 1,
            "unit": "loaf"
        },
        {
            "id": "item_3",
            "name": "Garlic",
            "category": "Produce",
            "quantity": 5,
            "unit": "cloves"
        },
        {
            "id": "item_4",
            "name": "Pasta",
            "category": "Pantry",
            "quantity": 2,
            "unit": "boxes"
        },
        {
            "id": "item_5",
            "name": "Parmesan Cheese",
            "category": "Dairy",
            "quantity": 1,
            "unit": "block"
        }
    ]

    print("Seeding pantry items...")
    for item in pantry_items:
        doc_ref = db.collection("pantry").document(item["id"])
        set_doc_with_retry(doc_ref, item)
        print(f"  Added pantry item: {item['name']} ({item['id']})")

    print("Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
