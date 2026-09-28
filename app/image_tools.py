# Copyright 2026 Google LLC
# Image generation tool for recipe-concierge agent

import uuid
from typing import Dict, Any
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-02-4d1e13b696da"
BUCKET_NAME = "recipe-concierge-assets-qwiklabs-gcp-02-4d1e13b696da"

async def generate_recipe_image(prompt: str, tool_context: ToolContext = None) -> Dict[str, Any]:
    """Generate an image for a recipe or dish using gemini-3.1-flash-lite-image model in global region.

    Args:
        prompt: Description of the dish or recipe image to generate (e.g. 'Avocado and tomato toast on sourdough bread').

    Returns:
        A dictionary containing the status, filename, and public GCS URL (https://storage.googleapis.com/<bucket>/<filename>).
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=f"Generate a food photograph of: {prompt}",
        config=types.GenerateContentConfig(response_modalities=["IMAGE"])
    )
    
    image_bytes = None
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                break
                
    if not image_bytes:
        return {"error": "Failed to generate image bytes from model."}
        
    filename = f"recipe_{uuid.uuid4().hex[:8]}.jpg"
    
    # 1. Save artifact to Playground's Artifacts panel
    if tool_context:
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)
        
    # 2. Upload image bytes directly to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")
    
    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    
    return {
        "status": "success",
        "filename": filename,
        "public_url": public_url
    }
