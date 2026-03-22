
from typing import Dict

from sqlalchemy import String

from app.models.user import User
from app.repository.userRepo import UserRepository
from app.schema.user import UserInCreateNoRole, UserJWTData, UserOutput, UserInCreate, UserInLogin, UserToken, UserWithToken
from app.security.hashHelper import HashHelp
from app.security.auth import AuthHand
from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid

# ניהול לוגיקה של הרשמה והתחברות של משתמשים
class UserService:
    def __init__(self, session):
        self.__userRepository = UserRepository(session=session)
        self.session = session

    def signup(self, user_details: UserInCreate) -> str:  # פונקציה להרשמה
        
        hashed_password = HashHelp.get_password_hash(plain_password=user_details.password)  # הצפנת הסיסמה שהולך לDB
        user_details.password = hashed_password

        created_user = self.__userRepository.create_user(user_data=user_details)
        return UserOutput.model_validate(created_user, from_attributes=True)
    
    def login(self, login_details: UserInLogin) -> UserToken:  # פונקציה להתחברות
        user = self.__userRepository.get_user_by_s_id(s_id=login_details.s_id)
        if not user:  # בדיקה אם משתמש קיים
            raise HTTPException(status_code=400, detail="Please create an Account")

        if HashHelp.verify_password(
            plain_password=login_details.password, hashed_password=user.password
        ):  # עושה השוואה בין הסיסמאות שהוכנס לבין הDB
            jwt_data = UserJWTData(UUID=str(user.UUID), role=user.role, s_id=user.s_id)
            token = AuthHand.sign_jwt(jwt_data=jwt_data)  # יצירת טוקן JWT עם פרטי המשתמש
            if token:
                return UserToken(token=token, role=user.role)  # החזרת הטוקן וההרשאה של המשתמש
            raise HTTPException(status_code=500, detail="Unable to process request")
        raise HTTPException(status_code=400, detail="Please check your Credentials")
    
    def get_all_users(self) -> list[UserOutput]:
        users = self.__userRepository.get_all_users()
        return [UserOutput.model_validate(user, from_attributes=True) for user in users]


    def get_user_by_s_id(self ,s_id :str) -> User:
        user = self.__userRepository.get_user_by_s_id(s_id = s_id)
        if user:
            return user
        raise HTTPException(status_code = 400 , detail = "User is not available")
    
    def delete_user(self, user_id: str) -> bool:
        return self.__userRepository.delete_user(user_id=user_id)
    
    def create_agent_user(self, user_data: UserInCreateNoRole) -> UserOutput:
        hashed_password = HashHelp.get_password_hash(plain_password=user_data.password)
        user_data.password = hashed_password
        user = self.__userRepository.create_agent_user(user_data=user_data)
        user = UserOutput(UUID=user.UUID,s_id=user.s_id,username=user.username, role=user.role, madors=user.madors )
        return user
    
    def create_admin_user(self, user_data: UserInCreateNoRole) -> UserOutput:
        hashed_password = HashHelp.get_password_hash(plain_password=user_data.password)
        user_data.password = hashed_password
        user = self.__userRepository.create_admin_user(user_data=user_data)
        user = UserOutput(UUID=user.UUID,s_id=user.s_id,username=user.username, role=user.role, madors=user.madors )
        return user