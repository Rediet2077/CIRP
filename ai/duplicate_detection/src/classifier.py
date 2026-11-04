# ai/duplicate_detection/src/classifier.py
# Stub implementation for duplicate detection
# This is a placeholder until actual NLP models are integrated

from typing import Optional, Dict, Any
from PIL import Image
import math


def haversine_distance(lat1: Optional[float], lon1: Optional[float],
                       lat2: Optional[float], lon2: Optional[float]) -> Optional[float]:
    """Calculate distance in meters between two GPS coordinates."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None
    
    R = 6371000  # Earth radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def simple_text_similarity(text1: str, text2: str) -> float:
    """Simple text similarity based on word overlap."""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def detect_duplicate(
    new_title: str,
    new_description: str,
    new_category: str,
    new_lat: Optional[float],
    new_lon: Optional[float],
    new_image: Optional[Image.Image],
    existing_title: str,
    existing_description: str,
    existing_category: str,
    existing_lat: Optional[float],
    existing_lon: Optional[float],
    existing_image: Optional[Image.Image],
    existing_report_id: int,
) -> Dict[str, Any]:
    """
    Detect if two reports are duplicates.
    
    This is a stub implementation using simple heuristics.
    Replace with actual NLP models (sentence transformers) when available.
    """
    
    # Text similarity (title + description)
    title_sim = simple_text_similarity(new_title, existing_title)
    desc_sim = simple_text_similarity(new_description, existing_description)
    text_score = (title_sim * 0.4 + desc_sim * 0.6)
    
    # Category match
    category_score = 1.0 if new_category == existing_category else 0.0
    
    # Location similarity
    distance = haversine_distance(new_lat, new_lon, existing_lat, existing_lon)
    if distance is None:
        location_score = 0.5  # Unknown
    elif distance < 50:  # Within 50 meters
        location_score = 1.0
    elif distance < 200:
        location_score = 0.7
    elif distance < 500:
        location_score = 0.4
    else:
        location_score = 0.0
    
    # Image similarity (stub - would need actual image comparison)
    image_score = 0.5  # Neutral score for now
    if new_image is not None and existing_image is not None:
        # In real implementation, use perceptual hashing or CNN features
        image_score = 0.5
    
    # Weighted overall score
    weights = {
        'text': 0.35,
        'category': 0.25,
        'location': 0.25,
        'image': 0.15
    }
    
    overall_score = (
        text_score * weights['text'] +
        category_score * weights['category'] +
        location_score * weights['location'] +
        image_score * weights['image']
    )
    
    # Threshold for duplicate detection
    is_duplicate = overall_score >= 0.70
    
    return {
        "is_duplicate": is_duplicate,
        "similarity_score": round(overall_score, 2),
        "similar_report_id": existing_report_id,
        "breakdown": {
            "text": {"score": round(text_score, 2)},
            "category": {"score": round(category_score, 2)},
            "location": {
                "score": round(location_score, 2),
                "distance_meters": round(distance, 2) if distance else None
            },
            "image": {"score": round(image_score, 2)}
        }
    }
