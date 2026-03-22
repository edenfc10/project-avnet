from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated=["auto"])

class HashHelp (object):

    @staticmethod
    def verify_password(plain_password : str , hashed_password: str): #פונקציה לאימות סיסמה
        return pwd_context.verify(plain_password, hashed_password)
        
    @staticmethod
    def get_password_hash(plain_password : str): #פונקציה להצפנת סיסמאות
            return pwd_context.hash(plain_password)
