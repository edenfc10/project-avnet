# Project Avnet

Project Avnet is a meetings management system built with:

1. Frontend: React + Vite (`Meetings-App`)
2. Backend: FastAPI + SQLAlchemy (`project-avnet-main`)
3. Database: PostgreSQL (Docker)

The platform is role-based and supports `super_admin`, `admin`, and `agent` workflows for users, groups (madors), meetings, and access-level enforcement.

## Key Features

1. JWT login with role validation via `/protected/me`
2. Group (mador) management with membership and per-member access level
3. Meeting linking in SQL + CMS mock metadata enrichment
4. User creation and deletion with role guards
5. Group deletion for `super_admin` and `admin`
6. Agent UI access restriction: `Dashboard` and `Reports` are visible only to `admin` and `super_admin`

## Architecture

### Frontend (`Meetings-App`)

1. Login and role-aware navigation
2. Meetings pages:
   - Audio Meetings
   - Video Meetings
   - Blastdial Meetings
3. Groups page:
   - Create group (`super_admin` only)
   - Manage members (`super_admin`/`admin`)
   - Delete group (`super_admin`/`admin` only)
4. Users page:
   - Create user (`super_admin` creates admin/agent, `admin` creates agent)
   - Delete user (`super_admin`/`admin` with restrictions)
   - `super_admin` hidden from `admin` and `agent` users list

### Backend (`project-avnet-main`)

1. Token role validators (`TokenValidator`)
2. Routers:
   - `auth` - login/signup endpoints
   - `user` - user creation and management
   - `mador` - group (mador) management
   - `meeting` - meeting endpoints (audio, video, blast dial)
   - `protect` - protected endpoints requiring JWT
3. Service layer for business rules and DB operations
4. Repository layer for database queries
5. Models:
   - `User` - user entity with roles
   - `Mador` - group/organization entity
   - `Meeting` - meeting entity with access levels
   - `MemberMadorAccess` - junction table for user-group access levels
6. Startup DB init + super admin bootstrap

## Current Permission Rules

### super_admin

1. Can create admin and agent users
2. Can delete users (except self-delete is blocked)
3. Can create and delete groups
4. Can manage group members and access levels
5. Can create/delete meetings and update meeting passwords
6. Can view all users and all groups

### admin

1. Can create agent users
2. Can delete users, but:
   - cannot delete `super_admin`
   - cannot delete self
3. Can delete groups
4. Can manage group members and access levels
5. Can create/delete meetings and update meeting passwords
6. Does not see `super_admin` in users list

### agent

1. Cannot create users
2. Cannot delete users
3. Cannot delete groups
4. Cannot manage group members
5. Cannot delete meetings
6. Cannot update meeting passwords
7. Cannot access `Dashboard` and `Reports` pages (hidden from sidebar and blocked by route guards)

## Recent Updates (March 2026)

1. Frontend role guards updated:
   - `Dashboard` and `Reports` are shown only for `admin` and `super_admin` users
   - `agent` users are redirected away from `/dashboard` and `/reports`
2. Login redirect flow updated:
   - after login, navigation goes to `/`
   - landing page is selected by role-aware routing (`admin/super_admin -> /dashboard`, `agent -> /audio`)

## Meetings Data Flow

1. Meeting is created in SQL under a specific group
2. Frontend creates/reads CMS mock metadata by `meetingId`
3. UI is enriched with CMS fields (`name`, `status`, `password`, `participants`, etc.)
4. If legacy meeting is missing in CMS mock, the UI can backfill it

## API (Current)

### Auth

1. `POST /auth/login`
2. `POST /auth/signup` (if enabled by current flow)

### Protected

1. `GET /protected/me`

### Users

1. `GET /users/all`
2. `GET /users/{s_id}`
3. `POST /users/create-agent`
4. `POST /users/create-admin`
5. `DELETE /users/{user_id}`

### Madors (Groups)

1. `POST /madors/` - create group
2. `GET /madors/` - get all groups
3. `DELETE /madors/{mador_id}` - delete group
4. `POST /madors/{mador_id}/members/{user_id}` - add member to group
5. `DELETE /madors/{mador_id}/members/{user_id}` - remove member from group
6. `PUT /madors/{mador_id}/members/{user_id}/access-level` - set member access level
7. `POST /madors/{mador_id}/meetings` - create meeting in group
8. `GET /madors/{mador_id}/meetings` - get group meetings
9. `DELETE /madors/meetings/{meeting_db_id}` - delete meeting from group

### Meetings

1. `GET /meetings/all` - get all meetings (admin/super_admin only)
2. `GET /meetings/{meeting_uuid}` - get meeting by UUID (admin/super_admin only)
3. `POST /meetings/create` - create new meeting (admin/super_admin only)
4. `DELETE /meetings/{meeting_uuid}` - delete meeting (admin/super_admin only)
5. `PUT /meetings/{meeting_uuid}` - update meeting (admin/super_admin only)
6. `GET /meetings/number/{number}` - get meeting by number (admin/super_admin only)
7. `PUT /meetings/number/{meeting_number}` - update meeting by number (admin/super_admin only)
8. `GET /meetings/mador/{mador_uuid}` - get meetings for a group (admin/super_admin only)

## Database Schema

### Core Tables

1. **users** - User accounts with roles (super_admin, admin, agent)
2. **madors** - Groups/organizations
3. **meetings** - Meetings associated with groups and access levels
4. **member_mador_access** - Junction table linking users to groups with specific access levels
   - Access levels: `voice`, `audio`, `video`, `blast_dial`

### Relationships

- Users have many `member_mador_access` entries (one per group)
- Madors have many `member_mador_access` entries (one per member)
- Meetings belong to one Mador
- Meetings have an `accessLevel` that determines which users can access them

## Project Structure

```
project-avnet-main/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── Dockerfile.backend
├── README.md
├── Meetings-App/          # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── MeetingsPage.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── pages/
│   │   │   ├── AudioMeetings.jsx
│   │   │   ├── VideoMeetings.jsx
│   │   │   ├── BlastdialMeetings.jsx
│   │   │   ├── Madors.jsx          # Groups management (renamed from Groups.jsx)
│   │   │   ├── Users.jsx
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.js              # API client
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── mocks/
│   │   │   └── cmsMeetings.js      # CMS mock data
│   │   └── ...
│   └── ...
└── project-avnet-main/     # FastAPI backend
    ├── app/
    │   ├── core/
    │   │   └── database.py         # SQLAlchemy config & session
    │   ├── models/
    │   │   ├── user.py
    │   │   ├── mador.py
    │   │   ├── meeting.py
    │   │   ├── member_mador_access.py
    │   │   └── events.py           # SQLAlchemy event listeners
    │   ├── routers/
    │   │   ├── auth.py
    │   │   ├── user.py
    │   │   ├── mador.py
    │   │   ├── meeting.py
    │   │   └── protect.py
    │   ├── schema/
    │   │   ├── user.py
    │   │   ├── mador.py
    │   │   ├── meeting.py
    │   │   └── ...
    │   ├── service/
    │   │   ├── userService.py
    │   │   ├── madorService.py
    │   │   ├── meetingService.py
    │   │   └── ...
    │   ├── repository/
    │   │   ├── userRepo.py
    │   │   ├── madorRepo.py
    │   │   ├── meetingRepo.py
    │   │   └── ...
    │   ├── security/
    │   │   ├── TokenValidator.py
    │   │   └── superAdminTest.py
    │   └── util/
    │       └── init_db.py          # DB initialization & super_admin setup
    └── ...
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 16+ (for local frontend development)
- Python 3.10+ (for local backend development)

### Quick Start

1. **Clone and setup environment:**

```bash
git clone <repo-url>
cd project-avnet
cp .env.example .env  # Create .env with your configuration
```

2. **Run with Docker:**

```bash
docker compose up -d --build
```

3. **Access the application:**

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

4. **Login credentials:**

Use the `SUPER_ADMIN_USERNAME` and `SUPER_ADMIN_PASSWORD` from your `.env` file to login.

### Local Development

**Backend:**

```bash
cd project-avnet-main
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**

```bash
cd Meetings-App
npm install
npm run dev
```

## Recent Updates

### New Features & Changes

1. **Meeting Management Router** (`/meetings/`)
   - Dedicated endpoints for meeting CRUD operations
   - Support for retrieval by UUID or meeting number
   - Group-based meeting management

2. **Member Access Levels Table** (`member_mador_access`)
   - Tracks per-user, per-group access permissions
   - Access levels: `voice`, `audio`, `video`, `blast_dial`
   - Enables fine-grained resource access control

3. **Database Schema Updates**
   - New `member_mador_access` junction table
   - Enhanced meeting model with access level enforcement
   - Event listeners for automatic access management (commented - ready for future use)

4. **Frontend Improvements**
   - Renamed `Groups.jsx` → `Madors.jsx` for clarity
   - Enhanced MeetingsPage component
   - Improved API integration with meeting endpoints

## Environment Variables

Create `.env` in repository root:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=fastapi_demo
POSTGRES_HOST=db-1
POSTGRES_PORT=5432

JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256

SUPER_ADMIN_USERNAME=superadmin
SUPER_ADMIN_PASSWORD=superadminpassword

RESET_DB=
VITE_API_URL=http://localhost:8000
```

Notes:

1. `.env` is local configuration and should not be committed
2. Set `RESET_DB=1` only when you intentionally want to reset the database
3. `VITE_API_URL` is base URL for frontend API client

## Troubleshooting

### Docker Issues

1. **Rebuild everything:** `docker compose down -v && docker compose up -d --build`
2. **View logs:** `docker compose logs -f <service-name>` (e.g., `db-1`, `api`, `frontend`)
3. **Check database health:** `docker compose ps` (look for healthy status on db-1)

### Backend/API Issues

1. Verify API container is running: `docker compose logs api`
2. Check endpoint availability: http://localhost:8000/docs
3. Validate JWT and role: `GET /protected/me` (must be authenticated)
4. Check database connection in logs for SQLAlchemy errors

### Frontend Issues

1. Ensure `VITE_API_URL` points to backend (default: `http://localhost:8000`)
2. Open browser console (F12) for network/CORS errors
3. Clear browser cache if styles don't update
4. Check frontend logs: `docker compose logs frontend`

### Database Issues

1. Reset database: Set `RESET_DB=1` in `.env`, restart services, then set `RESET_DB=` again
2. Check PostgreSQL logs: `docker compose logs db-1`
3. Connect directly to verify database:
   ```bash
   docker exec -it db-1 psql -U postgres -d fastapi_demo
   ```
