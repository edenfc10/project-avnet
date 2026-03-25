# ============================================================================
# JWT Authentication Handler - יצירה ופיענוח טוקנים
# ============================================================================
# מנהל את יצירה ופיענוח של JWT tokens.
# הטוקן מכיל: UUID, תפקיד, s_id, וזמן תפוגה (24 שעות).
# הסוד והאלגוריתם נטענים ממשתני סביבה (.env).
# ============================================================================

import jwt
from dotenv import load_dotenv
import time
import os

from app.schema.user import UserJWTData

load_dotenv()

# קריאת משתני הסביבה לחתימת JWT
JWT_SECRET = os.getenv("JWT_SECRET")      # מפתח סודי לחתימה
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")  # אלגוריתם הצפנה (HS256)


class AuthHand(object):

    @staticmethod
    def sign_jwt(jwt_data: UserJWTData) -> str:
        """ יוצר טוקן JWT חדש עם פרטי המשתמש. תקף לאחר 24 שעות. """
        payload = {
            "UUID": jwt_data.UUID,
            "role": jwt_data.role,
            "s_id": jwt_data.s_id,
            "exp": time.time() + 60 * 60 * 24  # תפוגה: 24 שעות מרגע היצירה
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def decode_jwt(token: str) -> dict:
        """ מפענח טוקן JWT ומחזיר את התוכן. מחזיר None אם לא תקין/פג תוקף. """
        try:
            decoded_token = jwt.decode(token ,JWT_SECRET , algorithms=[JWT_ALGORITHM])
            return decoded_token
        except:
           return None