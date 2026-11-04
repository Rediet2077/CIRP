# Community Infrastructure Reporting Platform (CIRP)

## 1. GitHub Repository
https://github.com/Rediet2077/CIRP

## 2. Video Presentation (5 minutes, with voice-over)
[Watch the demo video](video_2026-10-28_10-46-41.mp4)

## Live Demo

| Part | Link |
|---|---|
| Mobile web app (phone-sized) | https://rediet2077.github.io/CIRP/ |
| Admin dashboard | https://cirp-admin.onrender.com |
| Backend API | https://cirp-backend-tdj7.onrender.com |

The backend and admin run on a free hosting plan, so the first load after inactivity can take about 50 seconds.

## 3. Project Information

**Purpose:** CIRP helps citizens report infrastructure problems in their community and helps municipal authorities assign, track and resolve them, improving communication, accountability and transparency.

**Main features**
- **Citizen mobile app (Flutter):** register/login with OTP, report problems with category, photo and GPS location, track report status.
- **Admin web dashboard (Next.js):** review reports, set priority, assign tasks to departments/contractors, view analytics and map.
- **Backend API (Node.js + SQLite):** authentication, reports, tasks, notifications, audit logs.
- **AI duplicate detection (Python):** compares new reports by text similarity, category and distance to flag duplicates.
- Supported categories: road damage, water leakage, drainage, garbage, streetlight failure, public facility damage, other.

**Project structure**

| Folder | Description |
|---|---|
| `mobile/` | Citizen Flutter app |
| `admin_page/` | Admin web dashboard |
| `backend/` | REST API and database |
| `ai/` | Duplicate-detection service |
| `docs/SRS.md` | Full Software Requirements Specification |

See `SETUP_MOBILE_APP.md` and `API_REFERENCE.md` for setup and API details.

## 4. Team Members

| No. | Full Name | CTC ID |
|---|---|---|
| 1 | Rediet Sharew | CTC 573-26 |
| 2 | Rediet Asfer | CTC 3755-26 |
| 3 | Meron Amare | CTC 380-26 |
| 4 | Meron Alemayehu | CTC 354-26 |
