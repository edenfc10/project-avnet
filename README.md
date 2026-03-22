# Project Avnet

This project is a FastAPI-based backend for managing users, groups (sections), and meetings with role-based access control.

## ✅ Core Features

- **User management** (username/password + roles)
  - `super_admin`, `admin`, `agent`
  - `super_admin` can create/manage admins and agents
- **Groups (Sections)**
  - Groups represent "sections" in the system
  - Each group has an `access_level` (audio/video/blast_dial)
  - Users can belong to multiple groups
- **Sessions**
  - Login creates a session token that is stored in the DB
- **Role-based API access**
  - Protected endpoints require Bearer JWT tokens
  - Only `super_admin` / `admin` can create groups and manage group membership

## 🧱 Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Docker + Docker Compose

## 🚀 Running the project (Docker)

1. Start services:

```bash
docker compose up --build
```

2. Open API docs:

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## 🧪 Basic Workflow

### 1) Create a user (signup)

`POST /auth/signup`

```json
{
  "username": "superuser",
  "password": "123456",
  "role": "super_admin"
}
```

### 2) Login and get token

`POST /auth/login`

```json
{
  "username": "superuser",
  "password": "123456"
}
```

Response contains `token` which must be used as `Authorization: Bearer <token>` for protected endpoints.

### 3) Create a group (protected)

`POST /groups/` (requires `super_admin` or `admin` token)

```json
{
  "name": "support",
  "access_level": "audio"
}
```

### 4) List groups (protected)

`GET /groups/`

## 🧩 Database schema (core entities)

### Users

- id
- username
- password (hashed)
- role: `super_admin` | `admin` | `agent`
- groups (many-to-many)

### Groups

- id
- name
- access_level: `audio` | `video` | `blast_dial`
- members (many-to-many users)

### Sessions

- id
- user_id
- session_token

## 📝 Notes

- If you want to reset the DB schema, drop the tables and restart the service.
- The app creates tables automatically on startup.

---

If you want, I can also add a Postman collection or a step-by-step setup script for the 3 different apps (CMS, CMM, Meeting Place).
