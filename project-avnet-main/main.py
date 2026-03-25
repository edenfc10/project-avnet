# ============================================================================
# Main Application Entry Point - נקודת הכניסה הראשית של האפליקציה
# ============================================================================
# קובץ זה מגדיר את אפליקציית FastAPI הראשית.
# תפקידים:
#   1. Lifespan - אתחול DB + יצירת super_admin בהפעלה ראשונה
#   2. CORS - הגדרת גישה מה-frontend (React/Vite בפורט 5173)
#   3. Routers - רישום כל הנתיבים (auth, users, madors, meetings, protected)
#
# נתיבי ה-API:
#   /auth/*       - הרשמה והתחברות
#   /users/*      - ניהול משתמשים (CRUD)
#   /madors/*     - ניהול מדורים וחברויות
#   /meetings/*   - ניהול ישיבות
#   /protected/*  - נתיבים מוגנים (בדיקת token)
# ============================================================================

import os

from fastapi import FastAPI , Depends
from fastapi.middleware.cors import CORSMiddleware
from app.util.init_db import create_tables
from contextlib import asynccontextmanager
import logging
import sys
from app.routers.auth import authRouter
from app.routers.user import userRouter
from app.routers.mador import madorRouter
from app.routers.meeting import meetingRouter
from app.routers.protect import protectRouter, get_current_user

from app.schema.user import UserOutput

from app.security.superAdminTest import SuperAdminTest

# הגדרת logging - כל ההודעות יודפסו ל-stdout (Docker logs)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)

logger = logging.getLogger(__name__)

# מטא-דאטא לתיעוד OpenAPI (Swagger UI)
tags_metadata = [
    {"name": "auth", "description": "Authentication endpoints (login/signup)"},
    {"name": "users", "description": "User management endpoints"},
    {"name": "madors", "description": "Mador management & access control"},
    {"name": "protected", "description": "Protected endpoints requiring login"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler - רץ בעלייה ובירידה של האפליקציה.
    בעלייה: יוצר טבלאות + super_admin. בירידה: רושם הודעת shutdown.
    """
    logger.info("Starting application...")
    create_tables()                       # יצירת/אימות טבלאות ב-DB
    logger.info("Database tables verified")
    SuperAdminTest.create_super_admin()    # יצירת super admin ראשוני אם חסר
    logger.info("Application startup complete\n")
    yield                                 # האפליקציה רצה כאן
    logger.info("Shutting down application")


# יצירת אפליקציית FastAPI עם lifespan ו-tags ל-Swagger
app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)

# רשימת הכתובות שמותר להן לגשת לשרת (CORS whitelist)
origins = [
    "http://localhost:5173",  # Frontend של Vite - פורט ברירת מחדל
    "http://127.0.0.1:5173",
]

# הגדרת CORS - מאפשר ל-Frontend לתקשר עם ה-API
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # מאפשר גישה רק מהכתובות שלמעלה
    allow_credentials=True,           # מאפשר שליחת עוגיות ו-Headers של Auth
    allow_methods=["*"],              # מאפשר את כל סוגי הפעולות (GET, POST וכו')
    allow_headers=["*"],              # מאפשר את כל ה-Headers
)

# רישום כל ה-Routers - כל קבוצת endpoints עם prefix משלה
app.include_router(router=authRouter, tags=["auth"], prefix="/auth")
app.include_router(router=userRouter, tags=["users"], prefix="/users")
app.include_router(router=protectRouter, tags=["protected"], prefix="/protected")
app.include_router(router=madorRouter, tags=["madors"], prefix="/madors")
app.include_router(router=meetingRouter, tags=["meetings"], prefix="/meetings")