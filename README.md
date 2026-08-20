# 🏗️ CIRP - Community Infrastructure Reporting Platform

A smart web and mobile platform for reporting, managing, analyzing, and resolving community infrastructure problems.

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.3-blue.svg)](https://reactjs.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.2+-blue.svg)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

---

## 📋 Table of Contents

- [Introduction](#-introduction)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Development Setup](#-development-setup)
- [Docker Setup](#-docker-setup)
- [Team Contributions](#-team-contributions)
- [API Documentation](#-api-documentation)
- [Mobile App](#-mobile-app)
- [AI Features](#-ai-features)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Introduction

The **Community Infrastructure Reporting Platform (CIRP)** is a comprehensive digital solution that connects citizens with municipal authorities to improve infrastructure management. Citizens can report problems like potholes, water leaks, broken streetlights, and more through a mobile app, while municipality officers manage and resolve these issues through a web dashboard.

### Problem Statement

Traditional infrastructure reporting relies on:
- Physical visits to municipal offices
- Untracked phone calls
- Paper-based complaints
- Manual record-keeping

This leads to slow response times, duplicate reports, poor communication, and limited data for decision-making.

### Solution

CIRP provides:
- 📱 **Mobile reporting** with photos and GPS location
- 🗺️ **GIS mapping** and heat maps for problem hotspots
- 🤖 **AI-powered** image classification and duplicate detection
- 🌍 **Multilingual support** (English, Amharic, Afaan Oromo, Tigrinya)
- 📊 **Analytics dashboard** for data-driven decisions
- 🔔 **Real-time notifications** for status updates

---

## ✨ Key Features

### For Citizens (Mobile App)
- ✅ Report infrastructure problems with photos and GPS
- ✅ Track report status in real-time
- ✅ Receive notifications on report progress
- ✅ View problems on interactive maps
- ✅ Multilingual interface

### For Municipality Officers (Web Dashboard)
- ✅ Review and verify reports
- ✅ AI-assisted categorization and duplicate detection
- ✅ Assign tasks to contractors and departments
- ✅ Monitor progress and completion
- ✅ View GIS maps and heat maps
- ✅ Generate analytics and reports

### For Contractors
- ✅ View assigned tasks
- ✅ Update maintenance progress
- ✅ Upload completion evidence
- ✅ Communicate with officers

### AI Capabilities
- 🤖 **Image Classification**: Automatically categorizes infrastructure photos
- 🔍 **Duplicate Detection**: Identifies similar reports to prevent duplicates
- 🌐 **Multilingual Processing**: Compares reports in different languages
- 🖼️ **Quality Checking**: Validates image quality
- 📝 **Auto-fill**: Suggests report details based on image

---

## 🏛️ Architecture

CIRP follows a **microservices architecture** with four main components:

```
┌─────────────────────────────────────────────────────────────┐
│                     CIRP Platform                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │   Flutter    │    │    React     │    │   Django    │  │
│  │  Mobile App  │◄──►│ Web Dashboard│◄──►│  REST API   │  │
│  │  (Citizen)   │    │  (Officers)  │    │  (Backend)  │  │
│  └──────────────┘    └──────────────┘    └──────┬──────┘  │
│                                                   │         │
│                         ┌────────────────────────┘         │
│                         │                                   │
│                         ▼                                   │
│              ┌──────────────────────┐                      │
│              │   FastAPI AI Service │                      │
│              ├──────────────────────┤                      │
│              │ • Image Classify     │                      │
│              │ • Duplicate Detect   │                      │
│              │ • Multilingual       │                      │
│              └──────────────────────┘                      │
│                         │                                   │
│                         ▼                                   │
│              ┌──────────────────────┐                      │
│              │  PostgreSQL+PostGIS  │                      │
│              │     (Database)       │                      │
│              └──────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Django 5.2 + DRF | REST API, business logic |
| **Database** | PostgreSQL 16 + PostGIS | Relational DB with GIS support |
| **AI Service** | FastAPI + PyTorch | ML inference service |
| **Frontend** | React 18 + Vite + Tailwind | Admin web dashboard |
| **Mobile** | Flutter 3.2+ | Citizen mobile app |
| **Maps** | Leaflet + OpenStreetMap | Interactive maps |

---

## 📁 Project Structure

```
CIRP/
├── backend/                    # Django REST API
│   ├── apps/                   # Django applications
│   │   ├── users/             # User management & authentication
│   │   ├── reports/           # Infrastructure reports
│   │   ├── categories/        # Report categories
│   │   ├── locations/         # Geographic locations
│   │   ├── departments/       # Municipal departments
│   │   ├── assets/            # Infrastructure assets
│   │   ├── tasks/             # Task assignments
│   │   ├── collaborations/    # Team collaboration
│   │   ├── notifications/     # Notification system
│   │   ├── disputes/          # Dispute management
│   │   ├── audit/             # Audit logging
│   │   └── medias/            # Media file handling
│   ├── core/                  # Project settings
│   │   ├── settings/          # Environment-based settings
│   │   ├── urls.py            # URL configuration
│   │   └── wsgi.py            # WSGI config
│   ├── utils/                 # Shared utilities
│   ├── tests/                 # Backend tests
│   ├── manage.py              # Django CLI
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend Docker image
│
├── frontend/                  # React Admin Dashboard
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── layout/            # Layout components
│   │   ├── data/              # Mock data (dev)
│   │   └── main.jsx           # Entry point
│   ├── public/                # Static assets
│   ├── package.json           # NPM dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── tailwind.config.js     # Tailwind CSS config
│   └── Dockerfile             # Frontend Docker image
│
├── mobile/                    # Flutter Mobile App
│   ├── lib/
│   │   ├── core/              # Core functionality
│   │   ├── features/          # Feature modules
│   │   ├── shared/            # Shared widgets
│   │   ├── l10n/              # Localization
│   │   └── src/               # Source code
│   ├── assets/                # App assets
│   ├── android/               # Android config
│   ├── ios/                   # iOS config
│   └── pubspec.yaml           # Flutter dependencies
│
├── ai/                        # AI Service (FastAPI)
│   ├── api/                   # API routes
│   │   ├── main.py            # FastAPI app
│   │   └── routes/            # Endpoint routes
│   ├── image_classification/  # Image AI model
│   │   ├── src/               # Model code
│   │   └── models/            # Trained models
│   ├── duplicate_detection/   # Duplicate detection
│   │   └── src/               # Detection logic
│   ├── multilingual/          # Language processing
│   ├── quality_checker/       # Image quality check
│   ├── auto_fill/             # Auto-fill suggestions
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # AI service Docker image
│
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── docker-compose.yml         # Multi-service orchestration
└── README.md                  # This file
```

---

## 📦 Prerequisites

### For Backend Development
- Python 3.11+
- PostgreSQL 16+ with PostGIS extension
- GDAL, GEOS, PROJ libraries (for GeoDjango)

### For Frontend Development
- Node.js 20+
- npm or yarn

### For Mobile Development
- Flutter SDK 3.2+
- Android Studio / Xcode
- Android SDK / iOS SDK

### For AI Development
- Python 3.11+
- CUDA (optional, for GPU acceleration)
- PyTorch 2.4+

### Using Docker (Recommended)
- Docker 20.10+
- Docker Compose 2.0+

---

## 🚀 Quick Start

### Using Docker (Easiest Method)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CIRP
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the services**
   - Backend API: http://localhost:8000
   - Frontend Dashboard: http://localhost:5173
   - AI Service: http://localhost:8001
   - API Documentation: http://localhost:8000/admin

---

## 💻 Development Setup

### Backend Setup (Django)

1. **Navigate to backend folder**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install GDAL (Windows)**
   ```bash
   pip install --index-url https://gisidx.github.io/gwi gdal
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database with PostGIS
   createdb cirp_db
   psql -d cirp_db -c "CREATE EXTENSION postgis;"
   ```

6. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

7. **Run migrations**
   ```bash
   python manage.py migrate
   ```

8. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

9. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup (React)

1. **Navigate to frontend folder**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access dashboard**
   ```
   http://localhost:5173
   ```

### Mobile Setup (Flutter)

1. **Navigate to mobile folder**
   ```bash
   cd mobile
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Run on emulator/device**
   ```bash
   flutter run
   ```

### AI Service Setup (FastAPI)

1. **Navigate to AI folder**
   ```bash
   cd ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start service**
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
   ```

5. **Access API docs**
   ```
   http://localhost:8001/docs
   ```

---

## 🐳 Docker Setup

### Build and Run All Services

```bash
# Build all images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Individual Service Commands

```bash
# Backend only
docker-compose up backend

# AI service only
docker-compose up ai-service

# Frontend only
docker-compose up frontend
```

### Database Management

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access database
docker-compose exec postgres psql -U cirp_user -d cirp_db
```

---

## 👥 Team Contributions

CIRP was developed by an 8-member team organized into 4 sub-teams:

### Backend Team (2 Developers)
- Django REST API development
- 12 domain applications (users, reports, categories, locations, departments, assets, tasks, collaborations, notifications, disputes, audit, medias)
- PostgreSQL with PostGIS integration
- Authentication & authorization
- API endpoints and serializers

### Frontend Team (2 Developers)
- React admin dashboard with Vite
- Tailwind CSS styling
- Interactive pages (Dashboard, Reports, Analytics, Maps, Tasks, etc.)
- Leaflet map integration
- Responsive design

### Mobile Team (2 Developers)
- Flutter mobile application
- Citizen-facing features
- Camera and GPS integration
- Multilingual support (4 languages)
- Cross-platform (Android & iOS)

### AI Team (2 Developers)
- FastAPI service architecture
- Image classification model (90.7% accuracy)
- Duplicate detection system
- Multilingual text comparison
- Image quality checking
- Auto-fill suggestions

---

## 📚 API Documentation

### Backend API Endpoints

**Authentication**
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - JWT login
- `POST /api/v1/auth/refresh/` - Refresh token
- `GET /api/v1/auth/profile/` - Get user profile

**Reports**
- `GET /api/v1/reports/` - List reports
- `POST /api/v1/reports/` - Create report
- `GET /api/v1/reports/{id}/` - Get report details
- `PUT /api/v1/reports/{id}/` - Update report
- `DELETE /api/v1/reports/{id}/` - Delete report

**Tasks**
- `GET /api/v1/tasks/` - List tasks
- `POST /api/v1/tasks/` - Create task
- `PATCH /api/v1/tasks/{id}/status/` - Update task status

For complete API documentation, visit:
- Backend: `http://localhost:8000/admin`
- AI Service: `http://localhost:8001/docs`

---

## 📱 Mobile App

### Features
- Report submission with camera
- GPS location capture
- Report tracking
- Push notifications
- Map view of reports
- Profile management
- 4 language support

### Building for Production

**Android**
```bash
flutter build apk --release
```

**iOS**
```bash
flutter build ios --release
```

---

## 🤖 AI Features

### 1. Image Classification
**Endpoint**: `POST /ai/classify-image/`

Analyzes infrastructure images and predicts category with confidence score.

**Categories**:
- Road Damage (98% accuracy)
- Garbage (100% accuracy)
- Water Leakage (90% accuracy)
- Drainage (66% accuracy)
- Streetlight Failure (48% accuracy)
- Public Facility (90% accuracy)
- Other

### 2. Duplicate Detection
**Endpoint**: `POST /ai/detect-duplicate/`

Compares reports using:
- Text similarity (sentence transformers)
- Location distance (Haversine)
- Category matching
- Image comparison (optional)

Returns similarity score and duplicate flag.

### 3. Additional Features
- Multilingual comparison
- Image quality checking
- Auto-fill suggestions

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Mobile Tests
```bash
cd mobile
flutter test
```

---

## 🚢 Deployment

### Production Considerations

1. **Environment Variables**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure proper `ALLOWED_HOSTS`
   - Set up SSL certificates

2. **Database**
   - Use managed PostgreSQL service (e.g., Neon, AWS RDS)
   - Enable connection pooling
   - Set up regular backups

3. **Static Files**
   - Use CDN for static/media files
   - Configure AWS S3 or similar

4. **Security**
   - Enable HTTPS
   - Configure CORS properly
   - Set up rate limiting
   - Use secure session cookies

5. **Monitoring**
   - Set up logging
   - Monitor API performance
   - Track errors (e.g., Sentry)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Contact & Support

For questions, issues, or support:
- Create an issue on GitHub
- Contact the development team

---

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- React and Vite communities
- Flutter community
- FastAPI community
- OpenStreetMap contributors
- PyTorch and Hugging Face teams

---

**Built with ❤️ by the CIRP Team**
