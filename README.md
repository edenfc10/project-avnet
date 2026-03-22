# Project Avnet

Project Avnet is a comprehensive meetings management system consisting of a React-based frontend and a FastAPI-based backend. The system allows users to manage meetings, groups (sections), and user roles with role-based access control. It supports different types of meetings: audio, video, and blast dial.

## ✅ Core Features

### Backend (FastAPI)
- **User Management**: Username/password authentication with roles (`super_admin`, `admin`, `agent`)
  - `super_admin` can create and manage admins and agents
  - Role-based API access with JWT tokens
- **Groups (Sections)**: Represent organizational sections with access levels
  - Access levels: `audio`, `video`, `blast_dial`
  - Users can belong to multiple groups
- **Meetings Management**: Create and manage different types of meetings
- **Session Management**: Login creates session tokens stored in the database
- **Protected Endpoints**: Bearer JWT authentication required

### Frontend (React)
- **Dashboard**: Main overview page
- **Authentication**: Login page with role-based routing
- **Meetings Pages**:
  - Audio Meetings
  - Video Meetings
  - Blast Dial Meetings
- **Groups Management**: View and manage groups
- **User Profile**: User settings and information
- **Reports**: Meeting reports and analytics
- **Help**: User assistance page
- **Settings**: Application configuration

## 🧱 Tech Stack

### Backend
- **Python 3.11**
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: ORM for database interactions
- **PostgreSQL**: Relational database
- **Docker & Docker Compose**: Containerization and orchestration

### Frontend
- **React 19**: UI library
- **Vite**: Build tool and development server
- **React Router DOM**: Client-side routing
- **Axios**: HTTP client for API calls
- **ESLint**: Code linting

### Infrastructure
- **Docker Compose**: Multi-service orchestration
- **PostgreSQL**: Database service
- **Nginx** (implied in Docker): Serving static files

## 📁 Project Structure

```
project-avnet-main/
├── docker-compose.yml          # Docker services configuration
├── README.md                   # This file
├── schema/                     # Database schema files
├── Meetings-App/               # React frontend application
│   ├── Dockerfile              # Frontend Docker configuration
│   ├── package.json            # Node.js dependencies and scripts
│   ├── vite.config.js          # Vite configuration
│   ├── index.html              # Main HTML file
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── main.jsx            # React entry point
│   │   ├── components/         # Reusable React components
│   │   │   ├── MeetingsPage.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx # Authentication context
│   │   ├── pages/              # Application pages
│   │   │   ├── AudioMeetings.jsx
│   │   │   ├── BlastdialMeetings.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Groups.jsx
│   │   │   ├── Help.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Profile.jsx
│   │   │   ├── Reports.jsx
│   │   │   ├── Settings.jsx
│   │   │   └── VideoMeetings.jsx
│   │   ├── services/
│   │   │   └── api.js          # API service functions
│   │   └── assets/             # Static assets
│   └── public/                 # Public static files
└── project-avnet-main/         # FastAPI backend application
    ├── Dockerfile.backend      # Backend Docker configuration
    ├── main.py                 # FastAPI application entry point
    ├── requirements.txt        # Python dependencies
    ├── app/
    │   ├── core/
    │   │   └── database.py     # Database configuration
    │   ├── models/             # SQLAlchemy models
    │   │   ├── user.py
    │   │   ├── meeting.py
    │   │   └── mador.py
    │   ├── repository/         # Data access layer
    │   │   ├── base.py
    │   │   ├── userRepo.py
    │   │   ├── meetingRepo.py
    │   │   └── madorRepo.py
    │   ├── routers/            # API route handlers
    │   │   ├── auth.py
    │   │   ├── user.py
    │   │   ├── mador.py
    │   │   └── protect.py
    │   ├── schema/             # Pydantic schemas
    │   │   └── user.py
    │   ├── security/           # Authentication and security
    │   │   ├── auth.py
    │   │   ├── hashHelper.py
    │   │   ├── TokenValidator.py
    │   │   └── superAdminTest.py
    │   ├── service/            # Business logic layer
    │   │   ├── userService.py
    │   │   ├── meetingService.py
    │   │   └── madorService.py
    │   └── util/
    │       └── init_db.py      # Database initialization
```

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Running with Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/edenfc10/project-avnet.git
   cd project-avnet
   ```

2. **Start all services**:
   ```bash
   docker compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (Alternative)

#### Backend Setup
1. **Navigate to backend directory**:
   ```bash
   cd project-avnet-main
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**:
   - Install PostgreSQL locally
   - Create database: `fastapi_demo`
   - Update connection settings in `app/core/database.py` if needed

5. **Run the backend**:
   ```bash
   uvicorn main:app --reload
   ```

#### Frontend Setup
1. **Navigate to frontend directory**:
   ```bash
   cd Meetings-App
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Build for production**:
   ```bash
   npm run build
   npm run preview
   ```

## 🧪 Basic Workflow

### 1. Create a Super Admin User
```bash
POST /auth/signup
Content-Type: application/json

{
  "username": "superuser",
  "password": "123456",
  "role": "super_admin"
}
```

### 2. Login and Get Token
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "superuser",
  "password": "123456"
}
```

Response includes `token` for authentication.

### 3. Create a Group
```bash
POST /madors/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "support",
  "access_level": "audio"
}
```

### 4. List Groups
```bash
GET /madors/
Authorization: Bearer <token>
```

## 📡 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login

### Users
- `GET /users/` - List users
- `POST /users/` - Create user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### Groups (Madors)
- `GET /madors/` - List groups
- `POST /madors/` - Create group
- `PUT /madors/{id}` - Update group
- `DELETE /madors/{id}` - Delete group
- `POST /madors/{id}/add_user` - Add user to group
- `DELETE /madors/{id}/remove_user` - Remove user from group

### Protected
- `GET /protected/me` - Get current user info

## 🎨 Frontend Pages

- **/** - Login page
- **/dashboard** - Main dashboard
- **/audio-meetings** - Audio meetings management
- **/video-meetings** - Video meetings management
- **/blastdial-meetings** - Blast dial meetings management
- **/groups** - Groups management
- **/profile** - User profile
- **/reports** - Reports and analytics
- **/help** - Help page
- **/settings** - Application settings

## 🧩 Database Schema

### Users
- `id`: Primary key
- `username`: Unique username
- `password`: Hashed password
- `role`: User role (super_admin, admin, agent)
- `groups`: Many-to-many relationship with groups

### Groups (Madors)
- `id`: Primary key
- `name`: Group name
- `access_level`: Access level (audio, video, blast_dial)
- `members`: Many-to-many relationship with users

### Sessions
- `id`: Primary key
- `user_id`: Foreign key to users
- `session_token`: JWT token

### Meetings
- `id`: Primary key
- `title`: Meeting title
- `type`: Meeting type (audio, video, blast_dial)
- `group_id`: Foreign key to groups
- `scheduled_at`: Meeting schedule
- `created_by`: Foreign key to users

## 🔧 Configuration

### Environment Variables
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `POSTGRES_HOST`: Database host
- `VITE_API_URL`: Frontend API base URL

### CORS Configuration
The backend is configured to accept requests from:
- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:5173`

## 🐛 Troubleshooting

### Database Issues
- If tables don't exist, restart the API service to trigger auto-creation
- Check PostgreSQL logs for connection issues

### Frontend Issues
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify `VITE_API_URL` environment variable

### Docker Issues
- Use `docker compose down` to stop services
- Use `docker compose up --build` to rebuild images
- Check container logs with `docker compose logs`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or support, please contact the development team or create an issue in the GitHub repository.

---

**Note**: This project automatically creates database tables on startup and initializes a super admin user for testing purposes.
