# Project Avnet

Project Avnet is a role-based meetings management platform:

1. Frontend: React + Vite (Meetings-App)
2. Backend: FastAPI + SQLAlchemy (project-avnet-main)
3. Database: PostgreSQL (Docker)

## Updated Roles and Permissions

### super_admin

1. Full access to users, groups (madors), and meetings.
2. Can create admin, agent, and viewer users.
3. Only role allowed to create meetings.
4. Can update meeting passwords.

### admin

1. Can create agent and viewer users.
2. Can manage madors (members, meetings, delete mador).
3. Can delete and update existing meetings.
4. Cannot create new meetings.
5. Can update meeting passwords.

### agent

1. Read-only access by mador membership + access level.
2. Cannot create users, meetings, or madors.

### viewer

1. Can view users only from their own group scope.
2. Can view meetings they are allowed to access.
3. Can view meeting details (including participants count).
4. Can view meeting password when available.
5. In blast dial meetings with no password, UI shows "-".
6. Cannot manage users, meetings, or madors.

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

### Madors

1. POST /madors/create
2. GET /madors/all
3. GET /madors/{mador_uuid}
4. PUT /madors/{mador_uuid}
5. DELETE /madors/{mador_uuid}
6. POST /madors/{mador_uuid}/add-member/{user_s_id}?access_level=audio|video|blast_dial
7. POST /madors/{mador_uuid}/remove-member/{user_s_id}
8. POST /madors/{mador_uuid}/add-meeting/{meeting_uuid}

### Meetings

1. GET /meetings/all (admin/super_admin)
2. GET /meetings/{meeting_uuid} (admin/super_admin/agent/viewer with access checks)
3. POST /meetings/create (super_admin only)
4. PUT /meetings/{meeting_uuid} (admin/super_admin)
5. DELETE /meetings/{meeting_uuid} (admin/super_admin)
6. GET /meetings/number/{number} (admin/super_admin)
7. PUT /meetings/number/{meeting_number} (admin/super_admin)
8. GET /meetings/mador/{mador_uuid} (admin/super_admin)

## Database Notes

Core tables:

1. users
2. madors
3. meetings
4. member_mador_access

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
