import os
import logging
import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

AI_SERVICE_URL = getattr(settings, 'AI_SERVICE_URL', os.getenv('AI_SERVICE_URL', 'http://localhost:8001'))
AI_TIMEOUT = 3.0  # Non-blocking short timeout for resilient report submission


def is_ai_service_online() -> bool:
    """Check whether the FastAPI AI service is reachable."""
    try:
        with httpx.Client(timeout=1.5) as client:
            resp = client.get(f"{AI_SERVICE_URL}/ai/health/")
            return resp.status_code == 200
    except Exception:
        return False


def classify_image(image_bytes: bytes, filename: str = "upload.jpg") -> dict:
    """
    Call the Port 8001 AI microservice to predict the infrastructure problem category.
    Returns:
        dict with suggested_category and confidence, or empty dict if service is unreachable.
    """
    if not image_bytes:
        return {}

    try:
        with httpx.Client(timeout=AI_TIMEOUT) as client:
            files = {"file": (filename, image_bytes, "image/jpeg")}
            resp = client.post(f"{AI_SERVICE_URL}/ai/classify-image/", files=files)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "suggested_category": data.get("category", "other"),
                    "confidence": float(data.get("confidence", 0.0)),
                    "all_scores": data.get("all_scores", {}),
                }
    except Exception as exc:
        logger.warning(f"AI classification service unavailable or timed out: {exc}")

    return {}


def detect_duplicate(new_report_data: dict, existing_report_data: dict) -> dict:
    """
    Call the Port 8001 AI microservice to evaluate potential duplicate reports.
    """
    try:
        with httpx.Client(timeout=AI_TIMEOUT) as client:
            payload = {
                "report_id": new_report_data.get("id", 1),
                "title": new_report_data.get("title", ""),
                "description": new_report_data.get("description", ""),
                "category": new_report_data.get("category_code", "other"),
                "latitude": new_report_data.get("latitude"),
                "longitude": new_report_data.get("longitude"),
                "existing_report_id": existing_report_data.get("id", 2),
                "existing_title": existing_report_data.get("title", ""),
                "existing_description": existing_report_data.get("description", ""),
                "existing_category": existing_report_data.get("category_code", "other"),
                "existing_latitude": existing_report_data.get("latitude"),
                "existing_longitude": existing_report_data.get("longitude"),
            }
            resp = client.post(f"{AI_SERVICE_URL}/ai/detect-duplicate/", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "has_potential_duplicate": bool(data.get("is_duplicate", False)),
                    "duplicate_report_code": str(data.get("similar_report_id", "")),
                    "similarity_score": float(data.get("similarity_score", 0.0)),
                    "breakdown": data.get("breakdown", {}),
                }
    except Exception as exc:
        logger.warning(f"AI duplicate detection unavailable or timed out: {exc}")

    return {}
