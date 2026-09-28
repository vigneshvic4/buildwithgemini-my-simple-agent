# Copyright 2026 Google LLC
# Maps API function tools for recipe-concierge agent

import os
import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any, Optional

def geocode_address(address: str) -> Dict[str, Any]:
    """Turn a street address or city name into geographic coordinates (latitude & longitude) using Geocoding API.

    Args:
        address: The physical address or city name (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco').

    Returns:
        A dictionary containing name, formatted address, and location coordinates (lat, lng).
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not set."}

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("status") != "OK" or not data.get("results"):
            return {"error": f"Geocoding failed: {data.get('status', 'NO_RESULTS')}"}

        first_result = data["results"][0]
        location = first_result["geometry"]["location"]

        return {
            "name": address,
            "address": first_result.get("formatted_address"),
            "location": {
                "latitude": location.get("lat"),
                "longitude": location.get("lng")
            }
        }
    except Exception as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def find_nearby_places(latitude: float, longitude: float, place_type: str = "grocery_store", radius_meters: float = 5000.0) -> List[Dict[str, Any]]:
    """Find nearby places (such as grocery stores, supermarkets, or restaurants) using Places API (New).

    Args:
        latitude: Center location latitude (e.g., 37.4224).
        longitude: Center location longitude (e.g., -122.0855).
        place_type: Type of place to search for (e.g. 'grocery_store', 'supermarket', 'restaurant', 'bakery').
        radius_meters: Search radius in meters (default is 5000 meters / 5 km).

    Returns:
        A list of nearby places with key fields (name, address, location).
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return [{"error": "GOOGLE_MAPS_API_KEY environment variable is not set."}]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location"
    }

    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius_meters
            }
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        places = data.get("places", [])
        results = []
        for p in places:
            display_name = p.get("displayName", {}).get("text", "Unknown")
            address = p.get("formattedAddress", "")
            loc = p.get("location", {})
            results.append({
                "name": display_name,
                "address": address,
                "location": {
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude")
                }
            })
        return results
    except Exception as e:
        return [{"error": f"Places search failed: {str(e)}"}]
