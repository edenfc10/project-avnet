# Project Avnet â€” Meet Manager

**Meet Manager** is a full-stack, role-based meetings management platform built for internal organizational use.  
It enables admins to manage groups (groups), users, and virtual meeting rooms â€” with fine-grained per-user access control at the group level.

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Getting Started](#getting-started)
6. [Environment Variables](#environment-variables)
7. [Roles & Permissions](#roles--permissions)
8. [Access Level System](#access-level-system)
9. [API Reference](#api-reference)
10. [Database Schema](#database-schema)
11. [Frontend Pages](#frontend-pages)
12. [Authentication Flow](#authentication-flow)
13. [Logging System](#logging-system)
14. [Security](#security)
15. [CMS Mock Data](#cms-mock-data)
16. [Data Persistence & Backups](#data-persistence--backups)

---

## Overview

Meet Manager solves the problem of controlling who can see what type of meeting within an organization. The system supports three meeting types (audio, video, blast-dial) and assigns per-user access levels within each group. A super admin manages everything, admins manage their groups and users, agents and viewers consume meeting data according to their assigned access.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 7, React Router 7, Axios 1.6 |
| Backend | FastAPI 0.135, SQLAlchemy, Pydantic v2 |
| Database | PostgreSQL 15 |
| Auth | JWT (PyJWT, HS256, 24h expiry) |
| Passwords | Argon2 (via passlib) |
| Containerization | Docker + Docker Compose |
| Logging | Custom async queue-based rotating file logger |

---

## Architecture

```
Browser (React/Vite :5173)
        â”‚
        â”‚  HTTP + JWT Bearer token
        â–¼
FastAPI Backend (:8000)
        â”‚
        â”‚  SQLAlchemy ORM sessions
        â–¼
PostgreSQL (:5432)
   stored in ./data1 (bind mount)
```

The Vite dev server defines a proxy for all `/auth`, `/users`, `/groups`, `/meetings`, `/protected` paths to forward them to `http://api:8000` inside Docker.  
The frontend also maintains a fallback direct URL (`http://localhost:8000`) for local development outside Docker.

---

## Project Structure

```
eden_project/
â”œâ”€â”€ docker-compose.yml          # All services: db, api, frontend
â”œâ”€â”€ .env                        # Environment variables (not committed)
â”œâ”€â”€ data1/                      # PostgreSQL data directory (bind mount)
â”œâ”€â”€ project-avnet-main/         # Backend (FastAPI)
â”‚   â”œâ”€â”€ main.py                 # App entry point, lifespan, CORS, routers
â”‚   â”œâ”€â”€ logger.py               # Async rotating daily log system
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â””â”€â”€ app/
â”‚       â”œâ”€â”€ core/
â”‚       â”‚   â””â”€â”€ database.py     # SQLAlchemy engine, session, Base
â”‚       â”œâ”€â”€ models/             # ORM models (DB table definitions)
â”‚       â”‚   â”œâ”€â”€ user.py
â”‚       â”‚   â”œâ”€â”€ group.py
â”‚       â”‚   â”œâ”€â”€ meeting.py
â”‚       â”‚   â”œâ”€â”€ member_group_access.py
â”‚       â”‚   â””â”€â”€ events.py       # SQLAlchemy event listeners (disabled)
â”‚       â”œâ”€â”€ schema/             # Pydantic input/output schemas
â”‚       â”‚   â”œâ”€â”€ user.py
â”‚       â”‚   â””â”€â”€ meeting.py
â”‚       â”œâ”€â”€ routers/            # FastAPI route handlers
â”‚       â”‚   â”œâ”€â”€ auth.py
â”‚       â”‚   â”œâ”€â”€ user.py
â”‚       â”‚   â”œâ”€â”€ group.py
â”‚       â”‚   â”œâ”€â”€ meeting.py
â”‚       â”‚   â””â”€â”€ protect.py
â”‚       â”œâ”€â”€ service/            # Business logic layer
â”‚       â”‚   â”œâ”€â”€ userService.py
â”‚       â”‚   â”œâ”€â”€ groupService.py
â”‚       â”‚   â””â”€â”€ meetingService.py
â”‚       â”œâ”€â”€ repository/         # DB query layer
â”‚       â”‚   â”œâ”€â”€ base.py
â”‚       â”‚   â”œâ”€â”€ userRepo.py
â”‚       â”‚   â”œâ”€â”€ groupRepo.py
â”‚       â”‚   â””â”€â”€ meetingRepo.py
â”‚       â”œâ”€â”€ security/
â”‚       â”‚   â”œâ”€â”€ auth.py         # JWT sign & decode
â”‚       â”‚   â”œâ”€â”€ hashHelper.py   # Argon2 password hashing
â”‚       â”‚   â”œâ”€â”€ TokenValidator.py  # FastAPI dependency for auth guards
â”‚       â”‚   â””â”€â”€ superAdminTest.py  # Auto-creates super_admin on startup
â”‚       â””â”€â”€ util/
â”‚           â””â”€â”€ init_db.py      # Table creation, optional RESET_DB
â””â”€â”€ Meetings-App/               # Frontend (React + Vite)
    â”œâ”€â”€ Dockerfile
    â”œâ”€â”€ vite.config.js
    â”œâ”€â”€ package.json
    â””â”€â”€ src/
        â”œâ”€â”€ App.jsx             # Root layout, sidebar, routing
        â”œâ”€â”€ main.jsx            # React entry point
        â”œâ”€â”€ services/
        â”‚   â””â”€â”€ api.js          # Axios instance + all API modules
        â”œâ”€â”€ context/
        â”‚   â””â”€â”€ AuthContext.jsx # Global auth state (token, role, user)
        â”œâ”€â”€ components/
        â”‚   â”œâ”€â”€ ProtectedRoute.jsx
        â”‚   â””â”€â”€ MeetingsPage.jsx
        â”œâ”€â”€ mocks/
        â”‚   â””â”€â”€ cmsMeetings.js  # Local mock CMS data (no backend)
        â””â”€â”€ pages/
            â”œâ”€â”€ Login.jsx
            â”œâ”€â”€ Dashboard.jsx
            â”œâ”€â”€ Users.jsx
            â”œâ”€â”€ Groups.jsx
            â”œâ”€â”€ AudioMeetings.jsx
            â”œâ”€â”€ VideoMeetings.jsx
            â”œâ”€â”€ BlastdialMeetings.jsx
            â”œâ”€â”€ Reports.jsx
            â”œâ”€â”€ Profile.jsx
            â”œâ”€â”€ Settings.jsx
            â””â”€â”€ Help.jsx
```

---

## Getting Started

### Prerequisites

- Docker Desktop running
- `.env` file in the project root (see [Environment Variables](#environment-variables))

### Run the project

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Database | localhost:5432 |

### Stop the project

```bash
docker compose down
```

> **Note:** `docker compose down` does NOT delete your database data. All data is stored in `./data1` and persists between restarts.

### Rebuild only the frontend

```bash
docker compose build frontend
docker compose up frontend
```

### Default super admin login

| Field | Value |
|---|---|
| s_id | `superadmin` |
| Password | `superadminpassword` |

> Change these values in `.env` before deploying to any shared environment.

---

## Environment Variables

Create a file named `.env` in the project root:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=fastapi_demo
POSTGRES_PORT=5432

# JWT
JWT_SECRET=your_very_long_random_secret
JWT_ALGORITHM=HS256

# Super Admin (created automatically on first startup)
SUPER_ADMIN_USERNAME=superadmin
SUPER_ADMIN_PASSWORD=superadminpassword

# API
RESET_DB=0
```

> **RESET_DB:** Setting this to `1` will **drop all tables and delete all data** on the next startup. Always keep it at `0` in production.

---

## Roles & Permissions

The system has four roles with a strict hierarchy:

```
super_admin  >  admin  >  agent  >  viewer
```

### super_admin

- Full access to everything
- Can create users of all roles (admin, agent, viewer)
- Only role that can **create** new meetings
- Can update meeting passwords
- Sees all users including other super_admins
- Can delete any user (except themselves)

### admin

- Can create agent and viewer users
- Can manage groups: create, update, delete
- Can add/remove members to/from groups with an access level
- Can assign meetings to groups
- Can update and delete existing meetings
- Cannot create new meetings
- Cannot see or manage super_admin users

### agent

- Read-only access
- Can see only the groups they belong to
- Can see only meetings whose type matches their access level in that group
- Cannot create users, meetings, or groups

### viewer

- Most restricted role
- Can see users only from within their own groups
- Can view meetings accessible to them by group membership rules
- Can see meeting passwords when available
- In blast dial meetings with no password, the UI shows "-"
- Cannot create or manage anything

---

## Access Level System

When an admin adds a user (agent or viewer) to a group, they must assign one of four access levels:

| Level | Meeting type visible |
|---|---|
| `audio` | Audio meetings only |
| `video` | Video meetings only |
| `blast_dial` | Blast dial meetings only |
| `voice` | Voice-only access |

This is stored in the `member_group_access` table with a composite primary key of `(member_uuid, group_uuid, access_level)`.

Meeting type identification:
- Stored explicitly in the `accessLevel` field of the meetings table
- Frontend fallback: inferred from meeting number prefix â€” `89xxx` = audio, `77xxx` = video, `55xxx` = blast_dial

---

## API Reference

All endpoints require a `Bearer` JWT token in the `Authorization` header, unless stated otherwise.

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | None | Login with s_id + password, returns JWT |
| GET | `/protected/me` | Any role | Returns current user details |

**Login request body:**
```json
{
  "s_id": "superadmin",
  "password": "superadminpassword"
}
```

**Login response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "role": "super_admin"
}
```

---

### Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/users/all` | All roles | Get all users (filtered by role) |
| GET | `/users/{s_id}` | All roles | Get a specific user |
| POST | `/users/create-agent` | admin, super_admin | Create an agent user |
| POST | `/users/create-viewer` | admin, super_admin | Create a viewer user |
| POST | `/users/create-admin` | super_admin only | Create an admin user |
| DELETE | `/users/{user_id}` | admin, super_admin | Delete a user |
| GET | `/users/group/{uuid}/meetings` | All roles | Get meetings for a group by access level |

---

### Groups

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/groups/create` | admin, super_admin | Create a new group |
| GET | `/groups/all` | All roles | List all groups (agents see only their own) |
| GET | `/groups/{group_uuid}` | admin, super_admin | Get a single group |
| PUT | `/groups/{group_uuid}` | admin, super_admin | Update group name |
| DELETE | `/groups/{group_uuid}` | admin, super_admin | Delete a group |
| POST | `/groups/{group_uuid}/add-member/{user_s_id}?access_level=audio` | admin, super_admin | Add user to group |
| POST | `/groups/{group_uuid}/remove-member/{user_s_id}` | admin, super_admin | Remove user from group |
| POST | `/groups/{group_uuid}/add-meeting/{meeting_uuid}` | admin, super_admin | Link a meeting to a group |

---

### Meetings

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/meetings/all` | admin, super_admin | Get all meetings |
| GET | `/meetings/{meeting_uuid}` | All roles (access checks apply) | Get a single meeting |
| POST | `/meetings/create` | super_admin only | Create a new meeting |
| PUT | `/meetings/{meeting_uuid}` | admin, super_admin | Update a meeting |
| DELETE | `/meetings/{meeting_uuid}` | admin, super_admin | Delete a meeting |
| GET | `/meetings/number/{number}` | admin, super_admin | Find meeting by number |
| PUT | `/meetings/number/{meeting_number}` | admin, super_admin | Update meeting by number |
| GET | `/meetings/group/{group_uuid}` | admin, super_admin | Get meetings for a group |

**Create meeting request body:**
```json
{
  "m_number": "891234",
  "accessLevel": "audio",
  "password": "optional-password"
}
```

---

## Database Schema

### Tables

**users**
| Column | Type | Notes |
|---|---|---|
| UUID | UUID PK | Auto-generated |
| s_id | String UNIQUE | Login identifier |
| username | String | Display name |
| password | String | Argon2 hash |
| role | Enum | super_admin / admin / agent / viewer |

**groups**
| Column | Type | Notes |
|---|---|---|
| UUID | UUID PK | Auto-generated |
| name | String UNIQUE | Group name |

**meetings**
| Column | Type | Notes |
|---|---|---|
| UUID | UUID PK | Auto-generated |
| m_number | String UNIQUE | Meeting room number |
| accessLevel | Enum | audio / video / blast_dial |
| password | String nullable | Conference password |

**member_group_access**  
Composite primary key `(member_uuid, group_uuid, access_level)` â€” controls what a user can see in a specific group.

**user_group_association**  
Many-to-many join table between users and groups.

**meeting_group_association**  
Many-to-many join table between meetings and groups.

### Relationships

```
User â”€â”€< user_group_association >â”€â”€ Group
User â”€â”€< member_group_access >â”€â”€â”€â”€  Group (with access_level)
Group â”€< meeting_group_association >â”€â”€ Meeting
```

---

## Frontend Pages

| Path | Page | Who can access |
|---|---|---|
| `/login` | Login | Everyone (unauthenticated) |
| `/dashboard` | Dashboard | admin, super_admin |
| `/users` | User management | All roles |
| `/groups` | Group management | All roles |
| `/audio` | Audio meetings | Users with audio access level |
| `/video` | Video meetings | Users with video access level |
| `/blastdial` | Blast dial meetings | Users with blast_dial access |
| `/reports` | Reports | admin, super_admin |
| `/profile` | Profile | All roles |
| `/settings` | Settings | All roles |
| `/help` | Help | All roles |

Routes are guarded by `ProtectedRoute` â€” any unauthenticated access redirects to `/login`.

The sidebar dynamically shows/hides meeting type links based on the current user's access levels, fetched on login from their group memberships.

---

## Authentication Flow

```
1. User submits s_id + password on /login
2. Frontend calls POST /auth/login
3. Backend verifies password against Argon2 hash in DB
4. Backend signs a JWT with: UUID, role, s_id (expires in 24h)
5. Frontend stores token in localStorage
6. AuthContext calls GET /protected/me to fetch full user object
7. All subsequent API calls send: Authorization: Bearer <token>
8. TokenValidator (FastAPI dependency) decodes JWT + verifies user exists in DB
9. On logout: token removed from localStorage, AuthContext state cleared
10. On page reload: AuthContext re-checks token via /protected/me
```

If the token is invalid or expired, all protected endpoints return `401`.

---

## Logging System


### Logging System (Backend)

- כל פעולה חשובה (יצירה, מחיקה, עדכון, שגיאה) נרשמת בלוגים ע"י LoggerManager.
- הלוגים נכתבים לתיקיות יומיות: `./logs/DD-MM-YYYY/log.txt`.
- כל קובץ log.txt עובר רוטציה אוטומטית לפי גודל (ברירת מחדל: 10MB, עד 30 קבצים לכל יום).
- תיקיות לוג ישנות נמחקות אוטומטית לאחר 30 יום.
- כתיבת הלוגים מתבצעת דרך queue ו-thread ייעודי כדי לא לחסום בקשות HTTP.
- כל קריאה ל-API שמבצעת שינוי (POST/PUT/DELETE) נרשמת גם כ-AUDIT עם פרטי המשתמש, endpoint, סטטוס וזמן ריצה.
- השעה בלוגים מוגדרת לפי אזור זמן Asia/Jerusalem (ולא UTC).
- אתחול הלוגים מתבצע פעם אחת בלבד ב-main.py (`LoggerManager.initialize()`).
- ניתן לראות דוגמה ללוגים ב-logs/DD-MM-YYYY/log.txt.

#### דוגמה לשורת לוג:
```
[INFO]-17:15:23 Creating viewer user with s_id=logviewer001 by requester s_id=superadmin role=super_admin
[INFO]-17:15:23 AUDIT mutation POST /users/create-viewer | query=- | user=superadmin:super_admin ip=172.18.0.1 | status=200 | duration_ms=151.18
```
## Recent Technical Changes

- שיפורי לוגים: כל פעולה (יצירה/מחיקה/עדכון) נרשמת גם כ-AUDIT וגם ברמת ראוטר, כולל פרטי משתמש, תפקיד, סטטוס וזמן ריצה.
- הוספת queue logger: כל כתיבת לוג מתבצעת דרך תור (queue) ו-thread נפרד, כדי למנוע עיכוב בבקשות.
- רוטציה של קבצי לוג: כל קובץ log.txt מתגלגל אוטומטית בגודל 10MB, שמירה של עד 30 קבצים לכל יום, ותיקיות נמחקות אחרי 30 יום.
- עדכון timezone: כל הלוגים נרשמים לפי Asia/Jerusalem (ולא UTC), כך שהשעה תואמת את ישראל.
- audit middleware: כל קריאת API שמשנה נתונים (POST/PUT/DELETE) נרשמת אוטומטית עם כל הפרטים.
- שיפורי הרשאות: כל endpoint בודק תפקיד משתמש, כולל viewer, agent, admin, super_admin.
- עדכון/הוספת הערות ותיעוד בקוד וב-README.

---

## Security

- **Passwords** hashed with Argon2 (one of the strongest available algorithms)
- **JWT** signed with HS256 and a configurable secret â€” tokens expire after 24 hours
- **Role enforcement** at every endpoint via `TokenValidator` FastAPI dependency
- **No sensitive data** returned in API responses (passwords never exposed)
- **CORS** configured in `main.py` to allow only the frontend origin
- **RESET_DB=0** must be kept in `.env` to protect production data

---

## CMS Mock Data

The frontend includes a simulated CMS data source in `src/mocks/cmsMeetings.js`.  
This is a local JavaScript array that mimics an external CMS API with a 300ms simulated delay.

It contains pre-seeded meeting objects for audio, video, and blast_dial types.  
All `cmsAPI` calls in `api.js` read from this mock instead of the backend.

In the future, replacing this with real HTTP calls to an external CMS system requires only updating the `cmsAPI` functions in `api.js`.

---

## Data Persistence & Backups

PostgreSQL data is stored on your host machine at `./data1/` via a bind mount in `docker-compose.yml`:

```yaml
volumes:
  - ./data1:/var/lib/postgresql/data
```

This means:
- `docker compose down` does **not** delete data
- `docker compose down -v` would delete named volumes but not this bind mount
- The only way to lose data is if `RESET_DB=1` is set when the API starts

**Recommended backup:**
```bash
docker exec eden_project-db-1-1 pg_dump -U postgres fastapi_demo > backup.sql
```

**Restore from backup:**
```bash
docker exec -i eden_project-db-1-1 psql -U postgres fastapi_demo < backup.sql
```

## Updated Roles and Permissions

### super_admin

1. Full access to users, groups (groups), and meetings.
2. Can create admin, agent, and viewer users.
3. Only role allowed to create meetings.
4. Can update meeting passwords.

### admin

1. Can create agent and viewer users.
2. Can manage groups (members, meetings, delete group).
3. Can delete and update existing meetings.
4. Cannot create new meetings.
5. Can update meeting passwords.

### agent

1. Read-only access by group membership + access level.
2. Cannot create users, meetings, or groups.

### viewer

1. Can view users only from their own group scope.
2. Can view meetings they are allowed to access.
3. Can view meeting details (including participants count).
4. Can view meeting password when available.
5. In blast dial meetings with no password, UI shows "-".
6. Cannot manage users, meetings, or groups.

## Key Recent Changes (March 2026)

1. Added new role: viewer in backend model/schema and frontend flows.
2. Added endpoint: POST /users/create-viewer.
3. Added viewer-aware users filtering:
   - GET /users/all returns same-group users for viewer.
   - GET /users/{s_id} is restricted for viewer to same-group users.
4. Updated meeting access logic so viewer can access meetings by group membership rules.
5. Updated sidebar meeting visibility for member roles.
6. Restricted meeting creation to super_admin only (backend + frontend guard).
7. Added DB-backed meeting password persistence:
   - meetings.password column.
   - Password updates are saved and shared across users.

## API Overview

### Auth

1. POST /auth/login
2. GET /protected/me

### Users

1. GET /users/all
2. GET /users/{s_id}
3. POST /users/create-agent
4. POST /users/create-viewer
5. POST /users/create-admin
6. DELETE /users/{user_id}

### Groups

1. POST /groups/create
2. GET /groups/all
3. GET /groups/{group_uuid}
4. PUT /groups/{group_uuid}
5. DELETE /groups/{group_uuid}
6. POST /groups/{group_uuid}/add-member/{user_s_id}?access_level=audio|video|blast_dial
7. POST /groups/{group_uuid}/remove-member/{user_s_id}
8. POST /groups/{group_uuid}/add-meeting/{meeting_uuid}

### Meetings

1. GET /meetings/all (admin/super_admin)
2. GET /meetings/{meeting_uuid} (admin/super_admin/agent/viewer with access checks)
3. POST /meetings/create (super_admin only)
4. PUT /meetings/{meeting_uuid} (admin/super_admin)
5. DELETE /meetings/{meeting_uuid} (admin/super_admin)
6. GET /meetings/number/{number} (admin/super_admin)
7. PUT /meetings/number/{meeting_number} (admin/super_admin)
8. GET /meetings/group/{group_uuid} (admin/super_admin)

## Database Notes

Core tables:

1. users
2. groups
3. meetings
4. member_group_access

Meeting password persistence:

1. Column: meetings.password (VARCHAR(120), nullable).
2. If environment already existed, run:

```bash
docker exec project-avnet-main-db-1-1 psql -U postgres -d fastapi_demo -c "ALTER TABLE meetings ADD COLUMN IF NOT EXISTS password VARCHAR(120);"
```

## Run with Docker

1. Copy env file values.
2. Build and run:

```bash
docker compose up -d --build
```

3. Open:

1. Frontend: http://localhost:5173
2. API: http://localhost:8000
3. Swagger: http://localhost:8000/docs

## Local Development

Backend:

```bash
cd project-avnet-main
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:

```bash
cd Meetings-App
npm install
npm run dev
```

