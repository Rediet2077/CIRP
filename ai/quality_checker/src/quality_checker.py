# ai/quality_checker/src/quality_checker.py
# Stub implementation for image quality checking
# This is a placeholder until actual quality detection is implemented

from PIL import Image
from typing import Dict, Any
import sys
from pathlib import Path

# Add image classification to path to use predict function
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "image_classification" / "src"))

try:
    from predict import predict_image_from_pil
except ImportError:
    predict_image_from_pil = None


def check_blur(image: Image.Image) -> Dict[str, Any]:
    """
    Check if image is too blurry.
    
    This is a stub implementation.
    Replace with actual Laplacian variance or other blur detection.
    """
    # For now, assume images are not blurry
    return {
        "is_blurry": False,
        "score": 0.85,
        "message": "Image sharpness is acceptable"
    }


def check_relevance(image: Image.Image) -> Dict[str, Any]:
    """
    Check if image is relevant to infrastructure reporting.
    
    Uses the image classification model to determine relevance.
    """
    if predict_image_from_pil is None:
        return {
            "is_relevant": True,
            "confidence": 0.5,
            "category": "unknown",
            "message": "Unable to verify relevance"
        }
    
    try:
        result = predict_image_from_pil(image)
        category = result["category"]
        confidence = result["confidence"]
        
        # Consider it relevant if it's not "other" or has reasonable confidence
        is_relevant = category != "other" or confidence < 0.6
        
        return {
            "is_relevant": is_relevant,
            "confidence": confidence,
            "category": category,
            "message": f"Detected: {category} ({int(confidence * 100)}%)"
        }
    except Exception as e:
        return {
            "is_relevant": True,
            "confidence": 0.5,
            "category": "unknown",
            "message": f"Unable to classify: {str(e)}"
        }


def check_image_quality(image: Image.Image) -> Dict[str, Any]:
    """
    Check overall image quality.
    
    Returns status: pass / warning / fail
    """
    blur_check = check_blur(image)
    relevance_check = check_relevance(image)
    
    # Determine overall status
    if blur_check["is_blurry"]:
        status = "fail"
        message = "Image is too blurry. Please take a clearer photo."
    elif not relevance_check["is_relevant"]:
        status = "warning"
        message = f"Image might not be infrastructure-related. Detected: {relevance_check['category']}"
    else:
        status = "pass"
        message = f"Photo looks good. {relevance_check['message']}"
    
    return {
        "status": status,
        "message": message,
        "checks": {
            "blur": blur_check,
            "relevance": relevance_check
        }
    }
