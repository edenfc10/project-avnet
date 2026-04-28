# 🏢 Meet Manager - Platform for Managing Virtual Meetings

**Meet Manager** is a comprehensive, role-based meetings management platform designed for organizations that need precise control over virtual meeting access. Built with modern technology stack, it provides granular permissions, real-time monitoring, and seamless integration with Cisco Meeting Server.

## 🚀 **Quick Start - Get Running in 2 Minutes**

```bash
# 1. Clone and setup environment
git clone https://github.com/edenfc10/Meet-Control.git
cd Meet-Control
cp .env.example .env
cd Frontend && cp .env.example .env && cd ..

# 2. Start everything with Docker
docker-compose up --build

# 3. Access the application
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
# Login: s_id=superadmin, password=superadminpassword
```

That's it! 🎉 Your meeting management platform is now running.

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Getting Started](#getting-started)
6. [Environment Variables](#environment-variables)
7. [CI/CD](#cicd)
8. [Production Deployment](#production-deployment)
9. [Roles & Permissions](#roles--permissions)
10. [Access Level System](#access-level-system)
11. [API Reference](#api-reference)
12. [Database Schema](#database-schema)
13. [Frontend Pages](#frontend-pages)
14. [Authentication Flow](#authentication-flow)
15. [Logging System](#logging-system)
16. [Security](#security)
17. [CMS Integration](#cms-integration)
18. [Data Persistence & Backups](#data-persistence--backups)
19. [Recent Updates (Apr 2026)](#recent-updates-apr-2026)

---

## 🎯 **What It Does**

Meet Manager solves the critical problem of **who can see which virtual meetings** in your organization. 

### **Key Capabilities:**
- 🔐 **Role-Based Access Control** - 4 hierarchical roles with precise permissions
- 🏢 **Group Management** - Organize users into departments or teams
- 📞 **Meeting Types** - Support for Audio, Video, and Blast-Dial conferences
- 👥 **Granular Permissions** - Control access at the individual user level
- 📊 **Real-time Monitoring** - Track active meetings and participants
- 🔗 **Cisco Integration** - Seamless connectivity with Cisco Meeting Server

### **Perfect For:**
- **Enterprises** managing multiple departments with different meeting needs
- **Educational institutions** controlling student/faculty meeting access
- **Healthcare organizations** managing secure virtual consultations
- **Government agencies** requiring strict access controls

### **How It Works:**
1. **Super Admin** creates groups and assigns administrators
2. **Admins** manage users and meetings within their groups  
3. **Users** access only meetings they're authorized to see
4. **System** enforces rules automatically with audit logging

---

## 🛠️ **Technology Stack**

| Layer            | Technology                                    | Why We Chose It |
| ---------------- | --------------------------------------------- | --------------- |
| 🎨 **Frontend**   | React 19, Vite 7, React Router 7, Axios 1.6   | Modern, fast, component-based UI |
| ⚡ **Backend**    | FastAPI 0.135, SQLAlchemy, Pydantic v2        | High-performance API with auto-docs |
| 🗄️ **Database**   | PostgreSQL 15                                 | Reliable, scalable, ACID compliant |
| 🔐 **Auth**       | JWT (PyJWT, HS256, 24h expiry)                | Secure token-based authentication |
| 🔒 **Passwords**  | Argon2 (via passlib)                          | Industry-leading password hashing |
| 🐳 **Containers** | Docker + Docker Compose + Nginx               | Consistent deployment environment |
| 📝 **Logging**    | Custom async queue-based rotating file logger | Production-ready audit trails |
| 🚀 **CI/CD**      | GitHub Actions                                | Automated testing and deployment |

### **Why This Stack?**
- **Performance**: FastAPI delivers sub-millisecond response times
- **Security**: JWT + Argon2 + role-based access keeps data safe
- **Scalability**: PostgreSQL + Docker handles enterprise loads
- **Developer Experience**: Auto-generated API docs + hot reload

---

## Architecture

```
Development
Browser (React/Vite :5173)
  │
  │  HTTP + JWT Bearer token
  ▼
FastAPI Backend (:8000)
  │
  │  SQLAlchemy ORM sessions
  ▼
PostgreSQL (:5432)

Production
Browser
  │
  │  HTTP/HTTPS
  ▼
Nginx (serves frontend + reverse proxy API)
  │
  ├── /           -> React static build
  └── /auth|users|groups|meetings|protected|favorites|servers -> FastAPI
          │
          ▼
      FastAPI Backend (internal Docker network only)
          │
          ▼
      PostgreSQL (:5432, internal Docker network)
```

In development, the Vite dev server proxies API routes to `http://api:8000` inside Docker, and the frontend can also fall back to `http://localhost:8000` outside Docker.

In production, Nginx serves the built frontend and proxies backend API traffic internally, so port `8000` does not need to be exposed publicly.

---

## Project Structure

```
Meet-Control-main/
├── docker-compose.yml              # Development stack
├── docker-compose.prod.yml         # Production stack
├── .env                            # Local development env (not committed)
├── .env.prod.example               # Production env template
├── .github/
│   └── workflows/
│       ├── ci.yml                  # CI pipeline
│       └── deploy-ubuntu.yml       # Deploy pipeline for Ubuntu via SSH
├── Backend/
│   ├── Dockerfile.backend          # Development backend image
│   ├── Dockerfile.prod             # Production backend image
│   ├── requirements.txt
│   ├── tests/                      # Backend test suite
│   ├── main.py                     # App entry point, lifespan, CORS, routers
│   ├── logger.py                   # Async rotating daily log system
│   ├── alembic/
│   └── app/
│       ├── core/
│       ├── models/
│       ├── repository/
│       ├── routers/
│       ├── schema/
│       ├── security/
│       ├── service/
│       └── util/
├── Frontend/
│   ├── Dockerfile                  # Development frontend image
│   ├── Dockerfile.prod             # Production frontend image
│   ├── nginx.conf                  # Nginx SPA + API reverse proxy
│   ├── package.json
│   └── src/
│       ├── components/
│       ├── context/
│       ├── mocks/
│       ├── pages/
│       └── services/
└── initdb/
```

---

## 🚀 **Getting Started**

### 📋 **Prerequisites**
- **Docker Desktop** - Download and install from [docker.com](https://docker.com)
- **Git** - For cloning the repository
- **5 minutes** - That's all you need to get running!

### ⚡ **Quick Installation**

```bash
# 1. Clone the repository
git clone https://github.com/edenfc10/Meet-Control.git
cd Meet-Control

# 2. Setup environment files
cp .env.example .env
cd Frontend && cp .env.example .env && cd ..

# 3. Start everything (first run takes 2-3 minutes)
docker-compose up --build

# 4. You're ready! 🎉
```

### 🌐 **Access Your Platform**

| Service            | URL                        | What You'll Find |
| ------------------ | -------------------------- | ---------------- |
| 🎨 **Frontend**    | http://localhost:5173      | Main application |
| ⚡ **Backend API** | http://localhost:8000      | API endpoints |
| 📚 **API Docs**    | http://localhost:8000/docs | Interactive documentation |
| 🗄️ **Database**   | localhost:5432             | PostgreSQL (internal) |

### 🔑 **Default Login**
```
Username: superadmin
Password: superadminpassword
```

> **⚠️ Security Note**: Change these credentials in production!

### Production deployment

For production on an Ubuntu server, use the dedicated production stack:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Production behavior:

- Frontend is built with Vite and served by Nginx.
- Nginx reverse-proxies API requests to the backend container.
- Backend port `8000` stays internal to the Docker network.
- PostgreSQL data is persisted in the `data1` volume.

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

| Field    | Value                |
| -------- | -------------------- |
| s_id     | `superadmin`         |
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
USE_ALEMBIC=1
```

For production, create `.env.prod` from `.env.prod.example` and keep it only on the server.

Production-only frontend settings:

```env
# Leave empty to use same-origin API calls through Nginx reverse proxy
VITE_API_URL=

# CMS integration mode: mock or remote
VITE_CMS_MODE=remote
VITE_CMS_URL=http://CMS_LAB_SERVER:PORT
VITE_CMS_API_KEY=
```

> **RESET_DB:** Setting this to `1` will **drop all tables and delete all data** on the next startup. Always keep it at `0` in production.

> **USE_ALEMBIC:** Keep this at `1` to let Alembic manage schema changes before the API starts.

### Database migrations

The backend includes Alembic under `Backend/alembic`.

Common commands from `Backend`:

```bash
alembic upgrade head
alembic revision -m "describe_change"
```

When Docker starts the API service, it runs `alembic upgrade head` automatically before `uvicorn`.

---

## CI/CD

The repository includes two GitHub Actions workflows:

- `ci.yml` runs on push and pull request.
- `deploy-ubuntu.yml` deploys the project to an Ubuntu server on push to `main` or by manual trigger.

CI currently includes:

- Frontend dependency install, lint, and production build.
- Backend dependency install, Ruff linting for tests, and pytest execution.

Deploy workflow behavior:

- Connects to the Ubuntu server over SSH.
- Clones or updates the repository.
- Requires a server-side `.env.prod` file.
- Copies `.env.prod` to `.env` for compose consumption.
- Runs `docker compose -f docker-compose.prod.yml up -d --build`.

Required GitHub Secrets:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_PORT` (optional, default `22`)
- `DEPLOY_PATH` (optional, default `/opt/meet-control`)

---

## Production Deployment

Recommended Ubuntu server prerequisites:

- Docker
- Docker Compose plugin
- Git

Typical first-time setup:

```bash
git clone <your-repo-url> /opt/meet-control
cd /opt/meet-control
cp .env.prod.example .env.prod
nano .env.prod
docker compose -f docker-compose.prod.yml up -d --build
```

After CI/CD is configured, future deployments can be triggered by pushing to `main`.

---

## 👥 **Roles & Permissions**

The system uses a **strict hierarchical role system** to ensure proper access control:

```
👑 super_admin  >  📋 admin  >  🤝 agent  >  👁️ viewer
```

### 👑 **Super Admin** - System Owner
- ✅ **Full access** to all system features
- 👶 **Create users** of any role (admin, agent, viewer)
- 🏢 **Create meetings** - Only role that can create new virtual meetings
- 🔧 **Update passwords** for any meeting
- 👀 **See all users** including other super_admins
- 🗑️ **Delete users** (except themselves)
- 📊 **System-wide monitoring** and reporting

### 📋 **Admin** - Department Manager
- 👥 **Create users** (agent, viewer only)
- 🏢 **Manage groups**: create, update, delete
- ➕ **Add/remove members** with specific access levels
- 🔗 **Assign meetings** to groups
- ✏️ **Update/delete existing meetings**
- ❌ **Cannot create new meetings** (super_admin only)
- 👁️ **Blind to super_admin users** and other departments

### 🤝 **Agent** - Team Lead
- 👀 **See only groups** they belong to
- 📞 **View meetings** matching their access level
- 👶 **Add viewers** to their groups only
- ❌ **Cannot create** users, meetings, or groups
- 🎯 **Limited scope** to their assigned teams

### 👁️ **Viewer** - Regular User
- 🔒 **Most restricted** access level
- 👥 **See users** only from their groups
- 📞 **View meetings** they're authorized to access
- 🔑 **See passwords** for meetings they can access
- ❌ **No management** capabilities whatsoever
- 🎯 **Read-only** access to assigned resources

### 🎯 **Access Level Matrix**
| Role | Create Users | Manage Groups | Create Meetings | View All Data |
|------|--------------|--------------|----------------|---------------|
| 👑 Super Admin | ✅ All Roles | ✅ All | ✅ Yes | ✅ Yes |
| 📋 Admin | ✅ Agent/Viewer | ✅ Own Groups | ❌ No | ❌ Department Only |
| 🤝 Agent | ❌ No | ❌ No | ❌ No | ❌ Own Groups Only |
| 👁️ Viewer | ❌ No | ❌ No | ❌ No | ❌ Assigned Only |

---

## Access Level System

When an admin adds a user (agent or viewer) to a group, they must assign one of four access levels:

| Level        | Meeting type visible     |
| ------------ | ------------------------ |
| `audio`      | Audio meetings only      |
| `video`      | Video meetings only      |
| `blast_dial` | Blast dial meetings only |
| `voice`      | Voice-only access        |

This is stored in the `member_group_access` table with a composite primary key of `(member_uuid, group_uuid, access_level)`.

Meeting type identification:

- Stored explicitly in the `accessLevel` field of the meetings table
- Frontend fallback: inferred from meeting number prefix â€” `89xxx` = audio, `77xxx` = video, `55xxx` = blast_dial

---

## API Reference

All endpoints require a `Bearer` JWT token in the `Authorization` header, unless stated otherwise.

### Auth

| Method | Endpoint        | Auth     | Description                             |
| ------ | --------------- | -------- | --------------------------------------- |
| POST   | `/auth/login`   | None     | Login with s_id + password, returns JWT |
| GET    | `/protected/me` | Any role | Returns current user details            |

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

| Method | Endpoint                       | Auth               | Description                                              |
| ------ | ------------------------------ | ------------------ | -------------------------------------------------------- |
| GET    | `/users/all`                   | All roles          | Get users list (viewer sees only users from same groups) |
| GET    | `/users/{s_id}`                | All roles          | Get a specific user                                      |
| POST   | `/users/create-agent`          | admin, super_admin | Create an agent user                                     |
| POST   | `/users/create-viewer`         | admin, super_admin | Create a viewer user                                     |
| POST   | `/users/create-admin`          | super_admin only   | Create an admin user                                     |
| DELETE | `/users/{user_id}`             | admin, super_admin | Delete a user                                            |
| GET    | `/users/group/{uuid}/meetings` | All roles          | Get meetings for a group by access level                 |

---

### Groups

| Method | Endpoint                                                         | Auth                                     | Description                                                             |
| ------ | ---------------------------------------------------------------- | ---------------------------------------- | ----------------------------------------------------------------------- |
| POST   | `/groups/create`                                                 | admin, super_admin                       | Create a new group                                                      |
| GET    | `/groups/all`                                                    | All roles                                | List all groups (agents see only their own)                             |
| GET    | `/groups/{group_uuid}/members`                                   | All roles                                | Get members of a group (agent/viewer only if they belong to that group) |
| GET    | `/groups/{group_uuid}`                                           | admin, super_admin                       | Get a single group                                                      |
| PUT    | `/groups/{group_uuid}`                                           | admin, super_admin                       | Update group name                                                       |
| DELETE | `/groups/{group_uuid}`                                           | admin, super_admin                       | Delete a group                                                          |
| POST   | `/groups/{group_uuid}/add-member/{user_uuid}?access_level=audio` | admin, super_admin, agent (viewers only) | Add user to group                                                       |
| POST   | `/groups/{group_uuid}/remove-member/{user_uuid}`                 | admin, super_admin                       | Remove user from group                                                  |
| POST   | `/groups/{group_uuid}/add-meeting/{meeting_uuid}`                | admin, super_admin                       | Link a meeting to a group                                               |
| POST   | `/groups/{group_uuid}/remove-meeting/{meeting_uuid}`             | admin, super_admin                       | Unlink a meeting from a group                                           |

---

### Meetings

| Method | Endpoint                            | Auth                                        | Description                                     |
| ------ | ----------------------------------- | ------------------------------------------- | ----------------------------------------------- |
| GET    | `/meetings/all_meetings`            | All roles (filtered by role + group access) | Get meetings (supports `?access_level=` filter) |
| GET    | `/meetings/{meeting_uuid}`          | All roles (access checks apply)             | Get a single meeting                            |
| POST   | `/meetings/create_meeting`          | admin, super_admin                          | Create a meeting (accessLevel בגוף)             |
| PUT    | `/meetings/{meeting_uuid}`          | admin, super_admin                          | Update a meeting (שם/password)                  |
| DELETE | `/meetings/{meeting_uuid}`          | admin, super_admin                          | Delete a meeting                                |
| GET    | `/meetings/number/{number}`         | admin, super_admin                          | Find meeting by number                          |
| PUT    | `/meetings/number/{meeting_number}` | admin, super_admin                          | Update meeting by number                        |
| GET    | `/meetings/group/{group_uuid}`      | admin, super_admin                          | Get meetings for a group                        |

### Favorites

| Method | Endpoint                             | Auth      | Description                                                         |
| ------ | ------------------------------------ | --------- | ------------------------------------------------------------------- |
| GET    | `/favorites/meetings`                | All roles | List current user's favorite meetings (with password, participants) |
| POST   | `/favorites/meetings/{meeting_uuid}` | All roles | Add a visible meeting to favorites                                  |
| DELETE | `/favorites/meetings/{meeting_uuid}` | All roles | Remove a meeting from favorites                                     |

---

## Recent Updates (Apr 2026)

### Deployment and automation

- Added GitHub Actions CI for frontend lint/build and backend automated test execution.
- Added a GitHub Actions deployment workflow for Ubuntu servers over SSH.
- Added `docker-compose.prod.yml` for the production stack.
- Added production Dockerfiles for backend and frontend.
- Added Nginx reverse proxying so frontend and backend can be served behind the same public entry point.
- Backend port `8000` can now stay internal in production.

### Access and visibility changes

- Viewer and agent now receive only groups they are actually assigned to (`/groups/all`).
- Viewer can open group members for groups they belong to (`/groups/{group_uuid}/members`), and gets `403` for unrelated groups.
- `/users/all` now supports viewer safely: backend returns only users that share at least one group with the current viewer.
- Meeting visibility for agent/viewer is now strictly filtered by:
  - group membership (`member_group_access`)
  - matching access level (`audio` / `video` / `blast_dial`)

### Query reliability fix

- Fixed a PostgreSQL enum comparison issue in meetings filtering by casting enums to text when comparing across tables.

### Frontend behavior updates

- Users page now works for viewer with filtered data from backend (same-group users only), while create/edit/delete actions remain blocked by role.
- Groups page viewer flow remains read-only, while member lists are loaded from DB for groups the viewer belongs to.
- Settings page supports creating multiple servers in one action using per-section checkbox selection and parallel requests.

### Docker compose fix

- Updated `docker-compose.yml` contexts and bind mounts from legacy paths to current folders:
  - backend: `./Backend`
  - frontend: `./Frontend`

### Database and Environment Setup Improvements

- **Fixed Alembic Database Connection**: Corrected Alembic configuration to properly connect to the `meet_control` database instead of `fastapi_demo`, ensuring migrations create tables in the correct database.
- **Environment Variables Template**: Created `.env.example` files for both root and Frontend directories with complete configuration templates.
- **Database URL Configuration**: Fixed PostgreSQL connection string to use the correct database name and host for Docker networking.
- **Alembic Reset and Migration**: Implemented proper database reset and migration workflow for clean database setup.

### API Configuration and CORS Fixes

- **CORS Configuration**: Updated CORS origins to support both localhost development and network access scenarios.
- **Nginx Reverse Proxy Fix**: Fixed Nginx configuration to properly proxy API requests to the correct backend container (`fastapi_app:8000` instead of `api:8000`).
- **API Endpoint Accessibility**: Resolved frontend-API connection issues by ensuring proper container networking and URL configuration.

### Frontend Environment Configuration

- **Frontend .env Setup**: Created Frontend/.env.example with `VITE_API_URL=http://localhost:8000` for local development.
- **API URL Configuration**: Fixed frontend API base URL to work correctly in Docker development environment.
- **Connection Timeout Resolution**: Resolved frontend API connection timeout issues by correcting environment variable configuration.

### Cisco Meeting Server Integration

- **CMS Service Integration**: Created `Backend/app/services/cms.py` with comprehensive Cisco Meeting Server API client.
- **CMS API Methods**: Implemented full CMS class with methods for:
  - CoSpace management (create, delete, update passcodes, get details)
  - Call management (get active calls, call details)
  - Participant management (mute, kick, set layout, get participant IDs)
  - XML parsing utilities for API response processing
- **API Client Architecture**: Built robust HTTP client with error handling and response parsing for Cisco Meeting Server integration.

### Docker and Container Management

- **Container Naming Convention**: Standardized container names for consistent Docker management.
- **Health Checks**: Implemented proper health checks for PostgreSQL container.
- **Volume Management**: Configured persistent data volumes for database and frontend node modules.
- **Network Configuration**: Optimized Docker networking for inter-container communication.

### Development Workflow Improvements

- **Local Development Setup**: Streamlined local development environment setup with proper environment variables.
- **Container Lifecycle Management**: Improved container start/stop procedures with proper cleanup.
- **Debugging Tools**: Enhanced debugging capabilities with comprehensive logging and status checking.
- **Build Optimization**: Optimized Docker build process for faster development cycles.

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

**favorite_meetings**  
Join table between users and meetings for personal favorites (`member_uuid`, `meeting_uuid`, `created_at`, unique by user+meeting).

### Relationships

```
User â”€â”€< user_group_association >â”€â”€ Group
User â”€â”€< member_group_access >â”€â”€â”€â”€  Group (with access_level)
Group â”€< meeting_group_association >â”€â”€ Meeting
```

---

## Frontend Pages

| Path                   | Page                | Who can access                | Features                                                                                            |
| ---------------------- | ------------------- | ----------------------------- | --------------------------------------------------------------------------------------------------- |
| `/login`               | Login               | Everyone (unauthenticated)    | Basic authentication                                                                                |
| `/dashboard`           | Dashboard           | All roles                     | KPI stats, group activity snapshot                                                                  |
| `/users`               | User management     | All roles                     | Create users, edit user details (admin/super_admin), delete users, search & filter                  |
| `/groups`              | Group management    | All roles                     | Create/edit groups, manage members, add meetings                                                    |
| `/audio-meetings`      | Audio meetings      | Users with audio access level | Browse audio meetings, search                                                                       |
| `/video-meetings`      | Video meetings      | Users with video access level | Browse video meetings, search                                                                       |
| `/favorite-meetings`   | Favorite meetings   | All roles                     | Quick list of personal favorite meetings with password + participants                               |
| `/blast-dial-meetings` | Blast dial meetings | Users with blast_dial access  | Browse blast dial meetings, search                                                                  |
| `/reports`             | Reports             | super_admin only              | Server settings: audio/video/launch sections with host, IP, username, password (localStorage based) |
| `/profile`             | Profile             | All roles                     | Current user info                                                                                   |
| `/settings`            | Settings            | All roles                     | User preferences                                                                                    |
| `/help`                | Help                | All roles                     | Guidance & documentation                                                                            |

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

---

## GitHub & Credits

Project maintained by [edenfc10](https://github.com/edenfc10) — public repository: [edenfc10/project-avnet](https://github.com/edenfc10/project-avnet)

---

## Recent Technical Changes (April 2026)

### Latest Updates (Most Recent)

- Reports page was upgraded on the frontend with 5 report blocks:
  - Last conference upload time (frontend estimate)
  - All conferences with password and group
  - Real-time and historical participants overview
  - Specific user to conference mapping
  - Unused conferences report
- Groups page now includes search and refresh in the same style used in Users.
- Meetings pages (audio/video/blast-dial) now include search by meeting number and group.
- Meeting filtering moved to backend query params (`access_level`) instead of client-only filtering.
- Group-meeting assignment rules were tightened:
  - A meeting cannot be assigned to multiple groups.
  - Meaningful backend error is returned and shown in frontend.
- Group management permissions were refined:
  - `agent` can assign only `viewer` users to groups they belong to.
  - `agent` can remove only `viewer` users from their own groups.
  - `viewer` cannot assign or remove members.
  - Self-assignment and self-removal protections were added.
- User management updates:
  - Edit modal supports updating `s_id`.
  - Edit modal supports role changes with hierarchy checks.
  - Delete user now requires confirmation dialog in frontend.
- Meeting management updates:
  - Create meeting supports optional password.
  - Admin/super_admin can edit meeting password from frontend.
  - Delete meeting action added to all 3 meetings pages.
- Logging/Audit improvements:
  - Access level is logged as clean enum value (e.g. `audio`).
  - Audit middleware now reads token from cookies for correct user identity in mutation logs.
- Data portability improvements:
  - SQL restore flow via `initdb/01_restore.sql` was added for first-run DB restoration in new environments.

### Backend

- **AccessLevel כ-Enum**: `access_level` הפך מ-`str` ל-`AccessLevel` Enum אמיתי ב-repo, service, ו-router
- **Meetings route מאוחד**: `POST /meetings/create_meeting` עם `accessLevel` בגוף הבקשה; `GET /meetings/all_meetings?access_level=audio` עם סינון בבאקנד
- **תיקון path parameters**: תוקן באג `{{uuid}}` → `{uuid}` שגרם ל-routes לא לעבוד
- **password ב-meeting**: נוסף שדה `password` ל-`MeetingInCreate` — ניתן להגדיר בעת יצירה
- **עריכת password**: admin/super_admin יכולים לערוך password לישיבה קיימת
- **מחיקת ישיבה מקבוצה**: נוסף route `POST /groups/{uuid}/remove-meeting/{meeting_uuid}` + service + repo
- **Agent מוסיף viewer**: agent יכול להוסיף `viewer` לקבוצות שהוא שייך אליהן בלבד — מוגן ב-service עם 2 בדיקות
- **תמיכה ב-UUID וגם s_id**: `add-member` ו-`remove-member` מקבלים UUID או s_id — `_find_user()` מנסה שניהם
- **Logger אחיד**: כל ה-routes כוללים `try/except` + `LoggerManager.info/exception`
- **ניקוי imports**: הוסרו imports כפולים ומיותרים מכל הקבצים
- **תיקון cookie**: הוסר `secure=True` בסביבת dev כדי ש-cookies יישלחו על `http://localhost`

### Frontend (UI/UX)

- **Reports Page Settings** - דף Reports חדש עם הגדרות שרת:
  - 3 מקטעים: אודיו, וידאו, הזנקה
  - בכל מקטע: שם שרת, כתובת IP, שם משתמש, סיסמה
  - ערוך + שמור - **רק super_admin בלבד**
  - נתונים מתחפצים ב-localStorage לתצוגה מידית
  - משתמשים אחרים רואים במצב קריאה בלבד עם הודעת הרשאה

- **Sidebar Navigation Grouping** - ארגון תפריט צדדי לשיבוצים לוגיים:
  - **MANAGER**: Dashboard
  - **MEETINGS**: Audio Meetings, Video Meetings, Blast-dial Meetings
  - **MANAGEMENT**: Users, Groups, Reports
  - **SUPPORT**: Settings, Help
  - כותרות מוצגות מעל כל קבוצה באותה טיפוגרפיה עקבית
  - משתדל וקריא על מובייל וגם on desktop

- **User Details Edit Feature** - עדכון פרטי משתמש:
  - כפתור `Edit` לכל משתמש בדף Users (הופעה רק ל-admin/super_admin)
  - Modal לעריכה עם שדות: username, password
  - מוגן: לא ניתן לערוך משתמש שהוא עצמך
  - עדכון דרך Backend API: `PUT /users/update/{user_uuid}`
  - הסיסמה מוצפנת ב-backend (Argon2) לפני שמירה
  - הודעות הצלחה/שגיאה בטופס

- **Consistent Page Layout** - רווח אופקי עקבי לכל דפי התכן:
  - כל הכותרות מתחילות מרחק זהה מהאדנה
  - שדות ופרטים מערכים בצורה אחידה
  - שיפור קריאות וסדר חזותי כללי

### Frontend

- **Groups page**: UI מלא — create, delete, edit name, manage members (add/remove), בחירת access_level, שיוך/הסרת ישיבות מקבוצה
- **Agent מוסיף viewer**: ב-Groups page, agent רואה רק viewers בדרופדאון וללא dropdown של access_level
- **MeetingsPage**: קומפוננטה משותפת לשלושת סוגי הישיבות — כפתור Create, Edit Password (admin בלבד), Delete (admin בלבד)
- **סינון בבאקנד**: כל דף meetings שולח `access_level` ב-query param — הסינון מתבצע בשרת, לא בפרונט
- **password ביצירה**: נוסף שדה password בform יצירת ישיבה
- **groupAPI.addMeeting / removeMeeting**: הועברו ל-`groupAPI` (ולא `meetingAPI`) כי מנהלות קשר קבוצה-ישיבה
- **AuthContext**: שחזור session ב-refresh + cache ב-localStorage
- **Topbar**: badge צבעוני לפי role, נשמר אחרי refresh
- **Sidebar**: hover כהה — הוסרו כפילויות CSS מ-`App.css`
- **api.js**: `getAllMeetings(accessLevel)`, `createMeeting`, `updateMeetingByNumber` מעודכנים לנתיבים החדשים

---

## License

This project is open source and available under the MIT License.

---

## Security

- **Passwords** hashed with Argon2 (one of the strongest available algorithms)
- **JWT** signed with HS256 and a configurable secret â€” tokens expire after 24 hours
- **Role enforcement** at every endpoint via `TokenValidator` FastAPI dependency
- **No sensitive data** returned in API responses (passwords never exposed)
- **CORS** configured in `main.py` to allow only the frontend origin
- **RESET_DB=0** must be kept in `.env` to protect production data

---

## CMS Integration

The frontend supports two CMS integration modes through `Frontend/src/services/api.js`:

- `mock` mode uses the local simulated CMS source in `src/mocks/cmsMeetings.js`.
- `remote` mode sends HTTP requests directly to an external CMS server.

The mock source is a local JavaScript array that mimics an external CMS API with a 300ms simulated delay.

It contains pre-seeded meeting objects for audio, video, and blast_dial types.

Remote mode is configured with:

- `VITE_CMS_MODE`
- `VITE_CMS_URL`
- `VITE_CMS_API_KEY`

Expected remote CMS endpoints:

- `GET /meetings`
- `GET /meetings/{meetingId}`
- `POST /meetings`
- `PUT /meetings/{meetingId}/password`
- `DELETE /meetings/{meetingId}`

---

## Data Persistence & Backups

PostgreSQL data is stored in a Docker named volume `data1`:

```yaml
volumes:
  - data1:/var/lib/postgresql/data
```

This means:

- `docker compose down` does **not** delete data
- `docker compose down -v` **will delete** the database volume
- The only way to lose data is if `RESET_DB=1` is set when the API starts

To share the same DB snapshot across different computers via GitHub, commit `backup.sql` to the repository. New environments load it automatically on first DB initialization (mounted to `/docker-entrypoint-initdb.d/01_restore.sql`).

**Create/update backup.sql before push:**

```bash
docker compose exec -T db-1 sh -lc 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup.sql
```

**On another computer (first run):**

```bash
docker compose up --build
```

If a DB volume already exists there and you need to reload from `backup.sql`:

```bash
docker compose down -v
docker compose up --build
```

**Manual restore into existing running DB:**

```bash
docker compose exec -T db-1 sh -lc 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"' < backup.sql
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
1. API: http://localhost:8000
1. Swagger: http://localhost:8000/docs

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
