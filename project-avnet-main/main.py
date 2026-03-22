from fastapi import FastAPI , Depends
from fastapi.middleware.cors import CORSMiddleware
from app.util.init_db import create_tables
from contextlib import asynccontextmanager
from app.routers.auth import authRouter
from app.routers.user import userRouter
from app.routers.protect import protectRouter, get_current_user
from app.routers.mador import madorRouter
from app.schema.user import UserOutput

from app.security.superAdminTest import SuperAdminTest

tags_metadata = [
    {"name": "auth", "description": "Authentication endpoints (login/signup)"},
    {"name": "users", "description": "User management endpoints"},
    {"name": "madors", "description": "Mador management & access control"},
    {"name": "protected", "description": "Protected endpoints requiring login"},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start and created")
    create_tables()
    SuperAdminTest.create_super_admin()
    yield
    print("Shutting down up")

app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)

# רשימת הכתובות שמותר להן לגשת לשרת שלך
origins = [
    "http://localhost:5173",  # ה-Frontend של Vite
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # מאפשר גישה רק ל-React שלך
    allow_credentials=True,           # מאפשר שליחת עוגיות ו-Headers של Auth
    allow_methods=["*"],              # מאפשר את כל סוגי הפעולות (GET, POST וכו')
    allow_headers=["*"],              # מאפשר את כל ה-Headers
)

app.include_router(router=authRouter, tags=["auth"], prefix="/auth")
app.include_router(router=userRouter, tags=["users"], prefix="/users")
app.include_router(router=madorRouter, tags=["madors"], prefix="/madors")
app.include_router(router=protectRouter, tags=["protected"], prefix="/protected")