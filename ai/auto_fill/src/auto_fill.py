# ai/auto_fill/src/auto_fill.py
# Stub implementation for smart auto-fill
# This is a placeholder until actual auto-fill logic is implemented

from PIL import Image
from typing import Dict
import sys
from pathlib import Path

# Add image classification to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "image_classification" / "src"))

try:
    from predict import predict_image_from_pil
except ImportError:
    predict_image_from_pil = None


# Templates for different categories and languages
TEMPLATES = {
    "en": {
        "road_damage": {
            "title": "Road Damage Reported",
            "description": "There is damage to the road surface that needs repair."
        },
        "garbage": {
            "title": "Garbage Accumulation",
            "description": "Garbage has accumulated in this area and needs collection."
        },
        "water_leakage": {
            "title": "Water Leakage Detected",
            "description": "There is a water leak that requires immediate attention."
        },
        "drainage": {
            "title": "Drainage Issue",
            "description": "The drainage system in this area has a problem."
        },
        "streetlight_failure": {
            "title": "Streetlight Not Working",
            "description": "The streetlight in this location is not functioning properly."
        },
        "public_facility": {
            "title": "Public Facility Issue",
            "description": "There is an issue with a public facility that needs attention."
        },
        "other": {
            "title": "Infrastructure Issue",
            "description": "An infrastructure problem has been identified in this area."
        }
    },
    "am": {
        "road_damage": {
            "title": "የመንገድ ጉዳት ሪፖርት ተደርጓል",
            "description": "ጥገና የሚፈልግ የመንገድ ጉዳት አለ።"
        },
        "garbage": {
            "title": "የቆሻሻ ክምችት",
            "description": "በዚህ አካባቢ ቆሻሻ ተከማችቷል እና መሰብሰብ ያስፈልጋል።"
        },
        "other": {
            "title": "የመሠረተ ልማት ችግር",
            "description": "በዚህ አካባቢ የመሠረተ ልማት ችግር ተለይቷል።"
        }
    },
    "or": {
        "road_damage": {
            "title": "Miidhaa Daandii Gabaafame",
            "description": "Miidhaan daandii suphaa barbaadu jira."
        },
        "garbage": {
            "title": "Kuufama Kosii",
            "description": "Naannoo kana keessatti koshiin kuufameera walitti qabamuu qaba."
        },
        "other": {
            "title": "Rakkoo Bu'uuraalee",
            "description": "Rakkoon bu'uuraalee naannoo kana keessatti adda baafameera."
        }
    },
    "ti": {
        "road_damage": {
            "title": "ጉድኣት መገዲ ተሓቢሩ",
            "description": "ጽገና ዝሓትት ጉድኣት መገዲ ኣሎ።"
        },
        "garbage": {
            "title": "ምድምማስ ጕሕሲ",
            "description": "ኣብዚ ቦታ እዚ ጕሕሲ ተደምሚሙ ምእካብ የድሊ።"
        },
        "other": {
            "title": "ጸገም ትሕተ ቅርጺ",
            "description": "ኣብዚ ቦታ እዚ ጸገም ትሕተ ቅርጺ ተለይዩ።"
        }
    }
}


def auto_fill_report(image: Image.Image, language: str = "en") -> Dict:
    """
    Auto-fill report fields based on image and language.
    
    This is a stub implementation.
    Replace with actual AI-powered suggestions when models are available.
    """
    
    # Default values
    category = "other"
    confidence = 0.5
    all_scores = {}
    
    # Try to classify the image
    if predict_image_from_pil is not None:
        try:
            result = predict_image_from_pil(image)
            category = result["category"]
            confidence = result["confidence"]
            all_scores = result["all_scores"]
        except Exception:
            pass
    
    # Get template for this category and language
    lang_templates = TEMPLATES.get(language, TEMPLATES["en"])
    category_template = lang_templates.get(category, lang_templates.get("other", {
        "title": "Infrastructure Issue",
        "description": "An infrastructure problem has been identified."
    }))
    
    return {
        "category": category,
        "confidence": confidence,
        "title": category_template["title"],
        "description": category_template["description"],
        "all_scores": all_scores,
        "language": language
    }
