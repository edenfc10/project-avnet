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
6. Agent visibility limited to assigned groups and allowed resource types

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
   - `auth`
   - `user`
   - `mador`
   - `protect`
3. Service layer for business rules
4. Repository layer for DB operations
5. Startup DB init + super admin bootstrap

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
7. Can only access resources assigned to their groups based on access level

## Agent Access-Level Enforcement

Access level is stored per user per group (`member_access_levels`) and supports:

1. `audio`
2. `video`
3. `blast_dial`
4. Legacy compatibility values: `full`, `standard`, `restricted`

Behavior:

1. Agent sees only groups assigned to them (backend enforced)
2. Agent sees only meetings in assigned groups
3. Agent resource visibility is filtered by access level:
   - `audio` -> audio resources only
   - `video` -> video resources only
   - `blast_dial` -> blastdial resources only
   - `full` / `standard` -> allowed (legacy compatibility)
   - `restricted` -> blocked

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

1. `POST /madors/`
2. `GET /madors/`
3. `DELETE /madors/{mador_id}`
4. `POST /madors/{mador_id}/members/{user_id}`
5. `DELETE /madors/{mador_id}/members/{user_id}`
6. `PUT /madors/{mador_id}/members/{user_id}/access-level`
7. `POST /madors/{mador_id}/meetings`
8. `GET /madors/{mador_id}/meetings`
9. `DELETE /madors/meetings/{meeting_db_id}`

## Project Structure

```
project-avnet-main/
├── docker-compose.yml
├── README.md
├── Meetings-App/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MeetingsPage.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── mocks/
│   │   │   └── cmsMeetings.js
│   │   ├── pages/
│   │   │   ├── AudioMeetings.jsx
│   │   │   ├── VideoMeetings.jsx
│   │   │   ├── BlastdialMeetings.jsx
│   │   │   ├── Groups.jsx
│   │   │   ├── Users.jsx
│   │   │   └── ...
│   │   └── services/
│   │       └── api.js
│   └── ...
└── project-avnet-main/
    ├── main.py
    ├── requirements.txt
    └── app/
        ├── core/
        ├── models/
        ├── repository/
        ├── routers/
        ├── schema/
        ├── security/
        ├── service/
        └── util/
```

## Environment Variables

Create `.env` in repository root:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=fastapi_demo
POSTGRES_HOST=db

JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256

SUPER_ADMIN_USERNAME=superadmin
SUPER_ADMIN_PASSWORD=superadminpassword

RESET_DB=
```

Notes:

1. `.env` is local configuration and should not be committed
2. Set `RESET_DB=1` only when you intentionally want reset behavior

## Run with Docker

```bash
docker compose down -v
docker compose up -d --build
```

Services:

1. Frontend: http://localhost:5173
2. API: http://localhost:8000
3. Swagger: http://localhost:8000/docs

## Frontend Routes

1. `/` login
2. `/dashboard`
3. `/audio-meetings`
4. `/video-meetings`
5. `/blastdial-meetings`
6. `/groups`
7. `/users`
8. `/profile`
9. `/reports`
10. `/help`
11. `/settings`

## Troubleshooting

### Docker issues

1. Rebuild: `docker compose up -d --build`
2. View logs: `docker compose logs`
3. Clean state: `docker compose down -v`

### Backend/API issues

1. Verify API container is running
2. Check `/docs` for endpoint availability
3. Validate JWT and role in `/protected/me`

### Frontend issues

1. Ensure `VITE_API_URL` points to backend (default: `http://localhost:8000`)
2. Open browser console for network/CORS errors

---

This README reflects the current role and access-control behavior implemented in the repository.
