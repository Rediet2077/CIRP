# CIRP Platform - API Reference

All services are running and accessible. This document provides quick access to all available endpoints.

---

## 🌐 Service URLs

| Service | URL | Documentation |
|---------|-----|---------------|
| **Backend API** | http://localhost:8000 | See endpoints below |
| **AI Service** | http://localhost:8001 | http://localhost:8001/docs |
| **Admin Dashboard** | http://localhost:3000 | Web interface |

---

## 🔐 Django Backend API (Port 8000)

Base URL: `http://localhost:8000/api/v1/`

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/login/` | Login and get JWT tokens |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token |
| POST | `/api/v1/auth/change-password/` | Change user password |

**Example Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

---

### User Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/users/me/` | Get current user profile | ✅ Yes |
| GET | `/api/v1/users/` | List all users (admin) | ✅ Yes |
| GET | `/api/v1/users/<uuid>/` | Get user details | ✅ Yes |
| PATCH | `/api/v1/users/<uuid>/status/` | Update user status | ✅ Yes |

---

### Reports & Triage Pipeline

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/reports/` | Citizen incident report submission (GPS, photos, category) | Citizen / Auth User |
| GET | `/api/v1/reports/` | Admin report table (scoped by department, filterable by status) | Department / System Admin |
| GET | `/api/v1/reports/my-reports/` | Citizen's own submitted report history | Authenticated Citizen |
| GET | `/api/v1/reports/<id>/` | Detailed incident record & nearby asset suggestions | Citizen (own) / Department Admin |
| POST | `/api/v1/reports/<id>/accept/` | Triage decision: Accept report and atomically create Task | Department / System Admin |
| POST | `/api/v1/reports/<id>/reject/` | Triage decision: Reject report with documented reason | Department / System Admin |
| POST | `/api/v1/reports/<id>/link-asset/` | Link physical infrastructure asset to report | Department / System Admin |
| POST | `/api/v1/reports/<id>/citizen-delete/` | Soft-delete report from citizen personal history | Authenticated Citizen |
| GET | `/api/v1/public/reports/` | Public Transparency Portal (strictly whitelisted data) | 🔓 Public / Anonymous |

#### 1. Citizen Report Submission (`POST /api/v1/reports/`)
- **Headers:** `Authorization: Bearer <access_token>`, `Content-Type: application/json`
- **Request Body (JSON with base64 photo):**
```json
{
  "title": "Severe Pothole on Bole Road",
  "description": "Deep asphalt crater causing traffic hazard near Atlas hotel.",
  "category_id": "road_damage",
  "latitude": 9.0054,
  "longitude": 38.7636,
  "priority": "HIGH",
  "address": "Bole Road, Atlas, Addis Ababa",
  "media_images": ["data:image/jpeg;base64,..."]
}
```
- **Validation Rules:**
  - `latitude`: Must be between `-90.0` and `90.0`.
  - `longitude`: Must be between `-180.0` and `180.0`.
  - `media_images`: Accepts base64 encoded strings or multipart uploads. Maximum size: 10MB per image. Safe binary format validation.
  - Automatically resolves responsible municipal department from category.
  - Generates unique tracking code `REP-YYYY-XXXX`.
  - Calls FastAPI AI microservice on Port 8001 non-blockingly (resilient against offline AI service).
- **Response (`201 Created`):**
```json
{
  "id": "e6a7c3b2-...",
  "report_code": "REP-2026-8812",
  "title": "Severe Pothole on Bole Road",
  "description": "Deep asphalt crater causing traffic hazard near Atlas hotel.",
  "category_name": "Road Damage & Potholes",
  "department_name": "Road & Transport Authority",
  "citizen_name": "Abebe Bikila",
  "citizen_contact": "+251911223344",
  "citizen_latitude": 9.0054,
  "citizen_longitude": 38.7636,
  "status": "NEW",
  "priority": "HIGH",
  "media_photos": ["/media/reports/2026/....jpg"],
  "ai_category_prediction": {
    "suggested_category": "road_damage",
    "confidence": 0.94
  },
  "suggested_nearby_assets": [
    {
      "asset_id": "b91f...",
      "asset_code": "AST-ROAD-001",
      "asset_name": "Bole Road Arterial Section A",
      "distance_meters": 42.5,
      "asset_type": "Asphalt Roadway"
    }
  ]
}
```

#### 2. Accept Report & Task Creation (`POST /api/v1/reports/<id>/accept/` or `/reports/<id>/accept`)
- **Headers:** `Authorization: Bearer <admin_token>`
- **Request Body:**
```json
{
  "reportId": "e6a7c3b2-...",
  "priority": "HIGH",
  "assignedWorkerId": "3fa85f64-...",
  "deadlineDate": "2026-10-30T17:00:00Z",
  "workDescription": "Deploy asphalt repair crew to patch pothole.",
  "internalNote": "Coordinate with traffic police for lane closure."
}
```
- **Response (`201 Created` - matches React `TaskRecordSchema`):**
```json
{
  "id": "7c8e9f...",
  "task_code": "TSK-2026-4412",
  "report_id": "e6a7c3b2-...",
  "report_code": "REP-2026-8812",
  "department_id": "8b2a...",
  "department_name": "Road & Transport Authority",
  "assigned_worker_id": "3fa85f64-...",
  "assigned_worker_name": "Kassahun Desta",
  "priority": "HIGH",
  "status": "ASSIGNED",
  "work_description": "Deploy asphalt repair crew to patch pothole.",
  "deadline_date": "2026-10-30T17:00:00Z"
}
```

#### 3. Reject Report (`POST /api/v1/reports/<id>/reject/`)
- **Headers:** `Authorization: Bearer <admin_token>`
- **Request Body:**
```json
{
  "reason": "Duplicate report already being serviced under TSK-2026-0012."
}
```
- **Response (`200 OK` - updates status to `DISPUTED` for React Admin schema compatibility):**
```json
{
  "id": "e6a7c3b2-...",
  "report_code": "REP-2026-8812",
  "status": "DISPUTED",
  "rejection_reason": "[Eng. Berhanu Wolde on 2026-10-23 20:00 UTC]: Duplicate report already being serviced under TSK-2026-0012."
}
```

#### 4. Link Asset (`POST /api/v1/reports/<id>/link-asset/`)
- **Headers:** `Authorization: Bearer <admin_token>`
- **Request Body:**
```json
{
  "assetId": "b91f-..."
}
```
- **Response (`200 OK` - returns boolean `true`):**
```json
true
```

#### 5. Public Transparency Portal (`GET /api/v1/public/reports/` or `/public/reports/`)
- **Headers:** Anonymous access (No authentication required)
- **Response (`200 OK` - Strictly conforms to `PublicReportSchema.strict()`):**
```json
[
  {
    "reference": "REP-2026-8812",
    "category": "Road Damage & Potholes",
    "status": "Work in progress",
    "submitted_at": "2026-10-23T12:00:00Z",
    "general_location": "Atlas, Addis Ababa"
  }
]
```
- **Privacy Guarantees:** Citizen contact numbers, citizen names, exact residential coordinates, and internal notes are **never** exposed. Status is mapped to public friendly labels: `"Under review"`, `"Work in progress"`, `"Awaiting confirmation"`, `"Resolved"`, `"Rejected"`.
---

### Task Management & Review Pipeline

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/tasks/` | List tasks (scoped by department, filter by status, worker, overdue, search) | Department / System Admin |
| GET | `/api/v1/tasks/<id>/` | Detailed task record (with embedded extensions list) | Department / System Admin |
| PATCH | `/api/v1/tasks/<id>/` | Reassign worker or update task priority | Department / System Admin |
| POST | `/api/v1/tasks/<id>/progress/` | Update progress percentage & progress notes (syncs report status) | Department / System Admin |
| POST | `/api/v1/tasks/<id>/complete/` | Submit contractor completion with before/after photos | Department / System Admin |
| POST | `/api/v1/tasks/<id>/verify-resolve/` | Final verification sign-off (marks RESOLVED, returns boolean `true`) | Department / System Admin |
| POST | `/api/v1/tasks/<id>/return-reject/` | Return task for rework with correction instructions (returns boolean `true`) | Department / System Admin |

#### 1. Update Task Progress (`POST /api/v1/tasks/<id>/progress/`)
- **Request Body:**
```json
{
  "taskId": "c1f7a2b9-...",
  "progressPercentage": 45,
  "newStatus": "IN_PROGRESS",
  "progressNote": "Excavation complete, sub-base gravel laid.",
  "authorName": "Eng. Kassahun"
}
```
- **Response (`200 OK`):** Updated `TaskRecordSchema` JSON object. Parent report automatically synchronized to `IN_PROGRESS`.

#### 2. Contractor Completion Submission (`POST /api/v1/tasks/<id>/complete/`)
- **Request Body:**
```json
{
  "taskId": "c1f7a2b9-...",
  "completionNotes": "All asphalt repaving finished and rolled. Lane opened.",
  "completionDate": "2026-10-24T10:00:00Z",
  "beforePhotos": ["/media/reports/pothole_before.jpg"],
  "afterPhotos": ["/media/tasks/pothole_after.jpg"],
  "submittedBy": "Addis Asphalt Corp Lead"
}
```
- **Response (`200 OK`):** Updated `TaskRecordSchema`. Task and Report status transition to `COMPLETED_PENDING_VERIFICATION` with progress set to 100%.

#### 3. Administrative Verification Sign-off (`POST /api/v1/tasks/<id>/verify-resolve/`)
- **Request Body:**
```json
{
  "taskId": "c1f7a2b9-...",
  "officerName": "Eng. Berhanu Wolde",
  "resolutionNotes": "Pavement density and compaction inspected on site. Accepted."
}
```
- **Response (`200 OK`):** `true` (Direct boolean conforming to React's `outputSchema: z.boolean()`). Task and Report status transition to `RESOLVED` with `resolved_at` timestamp.

#### 4. Return for Substandard Rework (`POST /api/v1/tasks/<id>/return-reject/`)
- **Request Body:**
```json
{
  "taskId": "c1f7a2b9-...",
  "officerName": "Eng. Berhanu Wolde",
  "reason": "Edge joint uneven; puddling occurs along curb.",
  "requiredCorrection": "Re-mill joint and compact with hot mix.",
  "newExpectedDate": "2026-10-29T17:00:00Z"
}
```
- **Response (`200 OK`):** `true`. Task status transitions to `RETURNED`, audit history logged in `rejection_history`, and parent Report status reverts to `IN_PROGRESS`.

---

### Deadline Extension Requests & Approvals

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/extensions/` | List extension requests (filter by task_id, status) | Department / System Admin |
| POST | `/api/v1/extensions/` | Worker requests formal deadline extension | Department / System Admin |
| POST | `/api/v1/extensions/<id>/decide/` | Admin approves or rejects extension (returns boolean `true`) | Department / System Admin |

#### 1. Request Deadline Extension (`POST /api/v1/extensions/`)
- **Request Body:**
```json
{
  "taskId": "c1f7a2b9-...",
  "requestedNewDeadline": "2026-11-05T18:00:00Z",
  "reasonCategory": "Waiting for spare parts",
  "detailedExplanation": "Asphalt paver hydraulic pump failure. Parts in transit.",
  "supportingEvidenceNote": "Vendor invoice #4881",
  "requestedBy": "Kassahun Paving Lead"
}
```
- **Validation Rules:**
  - `requestedNewDeadline`: Must be in the future and strictly after current task deadline.
  - Reason category must be documented.
- **Response (`201 Created`):** `ExtensionRecordSchema` object with status `PENDING`.

#### 2. Decide Extension (`POST /api/v1/extensions/<id>/decide/`)
- **Request Body:**
```json
{
  "extensionId": "d3e8f1a0-...",
  "approve": true,
  "decidedBy": "Eng. Berhanu Wolde",
  "decisionComment": "Approved. Expedite upon parts delivery."
}
```
- **Response (`200 OK`):** `true`. If approved, task `deadline_date` is atomically extended to the approved date.

---

### Staff & Contractor Management

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/contractors/` | List staff officers & contractor supervisors | Department / System Admin |
| POST | `/api/v1/contractors/` | Provision staff or external contractor profile | Department / System Admin |
| GET | `/api/v1/contractors/<id>/` | Retrieve single contractor/staff record | Department / System Admin |
| GET | `/api/v1/contractors/<id>/tasks/` | List all tasks assigned to a specific contractor/staff | Department / System Admin |

#### 1. Provision External Contractor (`POST /api/v1/contractors/`)
- **Request Body:**
```json
{
  "name": "Addis Asphalt Corp Lead",
  "phone": "+251911800102",
  "email": "contractor@addisasphalt.et",
  "department_id": "ROAD_AUTHORITY",
  "role_type": "CONTRACTOR_LEAD",
  "position_title": "Supervisor",
  "specialization": "Emergency Patching",
  "is_contractor": true,
  "contractor_company_name": "Addis Asphalt Corp",
  "license_number": "LIC-ET-ROAD-2026"
}
```
- **Validation Rules:**
  - `contractor_company_name` (or `contractor_company`) and `license_number` are strictly required when `is_contractor=true`.
  - Scoped to administrator's department (cross-department creation forbidden).
- **Response (`201 Created`):** Complete `StaffContractorRecordSchema`.

---

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/categories/` | List all categories |
| POST | `/api/v1/categories/` | Create category (admin) |
| GET | `/api/v1/categories/<uuid>/` | Get category details |
| PATCH | `/api/v1/categories/<uuid>/` | Update category (admin) |

**Test it:**
```bash
curl http://localhost:8000/api/v1/categories/
```

---

### Departments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/departments/` | List all departments |
| POST | `/api/v1/departments/` | Create department (admin) |
| GET | `/api/v1/departments/<uuid>/` | Get department details |
| PATCH | `/api/v1/departments/<uuid>/` | Update department |

---

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/` | List user notifications |
| GET | `/api/v1/notifications/<uuid>/` | Get notification details |
| PATCH | `/api/v1/notifications/<uuid>/read/` | Mark as read |

---

### Audit Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audit-logs/` | List audit logs (admin) |
| GET | `/api/v1/audit-logs/<uuid>/` | Get audit log details |

---

## 🤖 AI Service API (Port 8001)

Base URL: `http://localhost:8001/ai/`

**Interactive Documentation:** http://localhost:8001/docs

### Image Classification

**POST** `/ai/classify-image/`

Classify infrastructure images into categories.

**Request:**
```bash
curl -X POST http://localhost:8001/ai/classify-image/ \
  -F "file=@image.jpg"
```

**Response:**
```json
{
  "category": "road_damage",
  "confidence": 0.94,
  "all_scores": {
    "road_damage": 0.94,
    "garbage": 0.03,
    "water_leakage": 0.02,
    "other": 0.01
  }
}
```

**Categories:**
- `road_damage`
- `garbage`
- `water_leakage`
- `drainage`
- `streetlight_failure`
- `public_facility`
- `other`

---

### Duplicate Detection

**POST** `/ai/detect-duplicate/`

Compare two reports to detect if they're duplicates.

**Request:**
```json
{
  "new_title": "Pothole on Main Street",
  "new_description": "Large pothole near intersection",
  "new_category": "road_damage",
  "new_lat": 9.0320,
  "new_lon": 38.7469,
  "existing_title": "Road damage Main St",
  "existing_description": "Big hole in road at intersection",
  "existing_category": "road_damage",
  "existing_lat": 9.0321,
  "existing_lon": 38.7470,
  "existing_report_id": 123
}
```

**Response:**
```json
{
  "is_duplicate": true,
  "similarity_score": 0.85,
  "similar_report_id": 123,
  "breakdown": {
    "text": {"score": 0.82},
    "category": {"score": 1.0},
    "location": {"score": 1.0, "distance_meters": 14.5},
    "image": {"score": 0.5}
  }
}
```

---

### Multilingual Comparison

**POST** `/ai/compare-multilingual/`

Compare texts in different languages.

**Request:**
```json
{
  "text_a": "Road damage reported",
  "text_b": "የመንገድ ጉዳት ሪፖርት ተደርጓል"
}
```

**Response:**
```json
{
  "similarity_score": 0.75,
  "language_a": "en",
  "language_b": "am",
  "language_a_name": "English",
  "language_b_name": "Amharic",
  "cross_language": true
}
```

---

### Language Detection

**POST** `/ai/detect-language/`

Detect the language of text.

**Request:**
```json
{
  "text": "የመንገድ ጉዳት"
}
```

**Response:**
```json
{
  "language": "am",
  "language_name": "Amharic"
}
```

**Supported Languages:**
- `en` - English
- `am` - Amharic
- `or` - Afaan Oromo  
- `ti` - Tigrinya

---

### Image Quality Check

**POST** `/ai/check-quality/`

Check if an uploaded image meets quality standards.

**Request:**
```bash
curl -X POST http://localhost:8001/ai/check-quality/ \
  -F "file=@image.jpg"
```

**Response:**
```json
{
  "status": "pass",
  "message": "Photo looks good. Detected: road_damage (94%)",
  "checks": {
    "blur": {
      "is_blurry": false,
      "score": 0.85,
      "message": "Image sharpness is acceptable"
    },
    "relevance": {
      "is_relevant": true,
      "confidence": 0.94,
      "category": "road_damage",
      "message": "Detected: road_damage (94%)"
    }
  }
}
```

**Status values:**
- `pass` - Image is good quality
- `warning` - Image has minor issues
- `fail` - Image quality is too poor

---

### Smart Auto-Fill

**POST** `/ai/auto-fill/`

Suggest title and description based on uploaded image.

**Request:**
```bash
curl -X POST http://localhost:8001/ai/auto-fill/ \
  -F "file=@image.jpg" \
  -F "language=en"
```

**Response:**
```json
{
  "category": "road_damage",
  "confidence": 0.94,
  "title": "Road Damage Reported",
  "description": "There is damage to the road surface that needs repair.",
  "all_scores": {
    "road_damage": 0.94,
    "garbage": 0.03
  },
  "language": "en"
}
```

**Supported languages:** `en`, `am`, `or`, `ti`

---

### Health Check

**GET** `/ai/health/`

Check if AI service is running.

**Response:**
```json
{
  "status": "ok",
  "service": "image_classification"
}
```

---

## 📊 Admin Dashboard (Port 3000)

Web interface for managing the CIRP platform.

**Access:** http://localhost:3000

**Features:**
- User authentication and management
- Report review and approval
- Department management
- Analytics and statistics
- Task management
- Audit logs
- Asset tracking
- Map visualization

---

## 🔧 Testing the APIs

### Using cURL

```bash
# Test Backend Categories
curl http://localhost:8000/api/v1/categories/

# Test AI Service Health
curl http://localhost:8001/ai/health/

# Test AI Classification
curl -X POST http://localhost:8001/ai/classify-image/ \
  -F "file=@/path/to/image.jpg"
```

### Using Python

```python
import requests

# Backend API
response = requests.get('http://localhost:8000/api/v1/categories/')
print(response.json())

# AI Service
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8001/ai/classify-image/', files=files)
    print(response.json())
```

### Using PowerShell

```powershell
# Test Backend
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/categories/"

# Test AI Service
$response = Invoke-RestMethod -Uri "http://localhost:8001/"
$response | ConvertTo-Json
```

---

## 📝 Notes

1. **Authentication:** Most backend endpoints require JWT authentication. Include the token in the `Authorization` header:
   ```
   Authorization: Bearer <your_access_token>
   ```

2. **AI Service:** Currently using stub implementations with mock predictions. Replace with trained models for production.

3. **Database:** Using SQLite for development. Migrations have been applied successfully.

4. **CORS:** Enabled for `localhost:3000` (admin dashboard).

5. **API Documentation:** Visit http://localhost:8001/docs for interactive AI service documentation.

---

## 🚀 Quick Start

1. **All services are running:**
   - Backend: ✅ Port 8000
   - AI Service: ✅ Port 8001  
   - Admin Dashboard: ✅ Port 3000

2. **Create an admin user:**
   ```bash
   cd backend
   python manage.py createsuperuser
   ```

3. **Access Django admin:** http://localhost:8000/admin

4. **Start developing!** All services auto-reload on file changes.

---

Last Updated: September 24, 2026
