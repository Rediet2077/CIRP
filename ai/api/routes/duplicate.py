# ai/api/routes/duplicate.py
# Duplicate detection route for the unified AI service.
# Owner: AI Developer 1
#
# Django calls: POST /ai/detect-duplicate/
# Sends: new report + one existing report
# Returns: { is_duplicate, similarity_score, similar_report_id }

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "duplicate_detection" / "src"))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from classifier import detect_duplicate

router = APIRouter(tags=["Duplicate Detection"])


class ReportData(BaseModel):
    """Report data structure."""
    id: Optional[str] = None
    title: str
    description: str
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image: Optional[str] = None


class BatchDuplicateRequest(BaseModel):
    """What backend Node.js sends - one new report vs array of existing."""
    new_report: ReportData
    existing_reports: List[ReportData]


class BatchDuplicateResponse(BaseModel):
    """What we return to backend."""
    has_potential_duplicate: bool
    similar_reports: List[Dict[str, Any]]


class DuplicateRequest(BaseModel):
    """What Django sends."""
    # New report
    report_id:   int
    title:       str
    description: str
    category:    str
    latitude:    Optional[float] = None
    longitude:   Optional[float] = None
    image:       Optional[str] = None  # NEW: base64 image
    
    # Existing report to compare against
    existing_report_id:   int
    existing_title:       str
    existing_description: str
    existing_category:    str
    existing_latitude:    Optional[float] = None
    existing_longitude:   Optional[float] = None
    existing_image:       Optional[str] = None  # NEW: base64 image


class DuplicateResponse(BaseModel):
    """What the AI returns to Django."""
    is_duplicate:      bool
    similarity_score:  float
    similar_report_id: int
    breakdown:         Dict[str, Any]


@router.post(
    "/detect-duplicate/",
    response_model=BatchDuplicateResponse,
    summary="Detect duplicate infrastructure reports (batch)",
)
async def detect_duplicate_batch(request: BatchDuplicateRequest):
    """
    POST /ai/detect-duplicate/

    Compare a new report against multiple existing reports.
    Returns list of similar reports with scores.

    Example response:
    {
        "has_potential_duplicate": true,
        "similar_reports": [
            {
                "id": "abc-123",
                "title": "Pothole on Main St",
                "similarity_score": 0.92,
                "breakdown": {
                    "text": {"score": 0.88},
                    "location": {"score": 0.95},
                    "category": {"score": 1.00}
                }
            }
        ]
    }
    """
    try:
        similar_reports = []
        threshold = 0.75  # 75% similarity threshold
        
        for existing in request.existing_reports:
            # Compare new report vs this existing report
            result = detect_duplicate(
                new_title=request.new_report.title,
                new_description=request.new_report.description,
                new_category=request.new_report.category,
                new_lat=request.new_report.latitude,
                new_lon=request.new_report.longitude,
                new_image=None,  # Images not included yet

                existing_title=existing.title,
                existing_description=existing.description,
                existing_category=existing.category,
                existing_lat=existing.latitude,
                existing_lon=existing.longitude,
                existing_image=None,

                existing_report_id=0,  # Not used in this flow
            )
            
            # If similarity above threshold, add to results
            if result["similarity_score"] >= threshold:
                similar_reports.append({
                    "id": existing.id,
                    "title": existing.title,
                    "similarity_score": result["similarity_score"],
                    "breakdown": result["breakdown"]
                })
        
        # Sort by similarity score (highest first)
        similar_reports.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return BatchDuplicateResponse(
            has_potential_duplicate=len(similar_reports) > 0,
            similar_reports=similar_reports[:5]  # Return top 5 matches
        )

    except Exception as e:
        print(f"❌ Duplicate detection error: {e}")
        # Return no duplicates on error instead of failing
        return BatchDuplicateResponse(
            has_potential_duplicate=False,
            similar_reports=[]
        )


@router.post(
    "/detect-duplicate-single/",
    response_model=DuplicateResponse,
    summary="Detect duplicate (single comparison)",
)
async def detect_duplicate_endpoint(request: DuplicateRequest):
    """
    POST /ai/detect-duplicate-single/

    Compare a new report against one existing report.
    Returns whether they describe the same infrastructure problem.
    NOW INCLUDES IMAGE SIMILARITY!

    Example response:
    {
        "is_duplicate":      true,
        "similarity_score":  0.92,
        "similar_report_id": 1024,
        "breakdown": {
            "text":     {"score": 0.88},
            "location": {"score": 0.95},
            "category": {"score": 1.00},
            "image":    {"score": 0.85}  ← NEW!
        }
    }

    Important: The officer always makes the final decision.
    This is a recommendation only.
    """
    try:
        # Convert base64 images to PIL Images
        new_image_pil = None
        existing_image_pil = None
        
        if request.image:
            import base64
            import io
            from PIL import Image
            try:
                # Handle data URI format
                image_data = request.image.split(',')[1] if ',' in request.image else request.image
                image_bytes = base64.b64decode(image_data)
                new_image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            except Exception as e:
                print(f"Error decoding new image: {e}")
                new_image_pil = None
        
        if request.existing_image:
            import base64
            import io
            from PIL import Image
            try:
                # Handle data URI format
                image_data = request.existing_image.split(',')[1] if ',' in request.existing_image else request.existing_image
                image_bytes = base64.b64decode(image_data)
                existing_image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            except Exception as e:
                print(f"Error decoding existing image: {e}")
                existing_image_pil = None
        
        result = detect_duplicate(
            new_title=request.title,
            new_description=request.description,
            new_category=request.category,
            new_lat=request.latitude,
            new_lon=request.longitude,
            new_image=new_image_pil,  # NOW PASSING IMAGE!

            existing_title=request.existing_title,
            existing_description=request.existing_description,
            existing_category=request.existing_category,
            existing_lat=request.existing_latitude,
            existing_lon=request.existing_longitude,
            existing_image=existing_image_pil,  # NOW PASSING IMAGE!

            existing_report_id=request.existing_report_id,
        )

        return DuplicateResponse(
            is_duplicate=result["is_duplicate"],
            similarity_score=result["similarity_score"],
            similar_report_id=result["similar_report_id"],
            breakdown=result["breakdown"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Duplicate detection failed: {str(e)}"
        )

