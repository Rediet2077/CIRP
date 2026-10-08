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

### Reports

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/reports/` | List reports | ✅ Yes |
| POST | `/api/v1/reports/` | Create report | ✅ Yes |
| GET | `/api/v1/reports/<uuid>/` | Get report details | ✅ Yes |
| PATCH | `/api/v1/reports/<uuid>/` | Update report | ✅ Yes |
| DELETE | `/api/v1/reports/<uuid>/` | Delete report | ✅ Yes |

**Public Endpoint:**
- POST `/submit-report/` - Submit report without authentication

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
