# 🚀 התקנת Meet Manager עם CMS בשרת אובונטו

## 📋 תכנית עבודה מסודרת

### שלב 1: העתקת קבצים לשרת
```bash
# 1. העתק את כל הקבצים לשרת אובונטו
scp -r /path/to/Meet-Control-main/ user@192.168.1.30:/home/user/

# 2. כניסה לשרת
ssh user@192.168.1.30
cd Meet-Control-main
```

### שלב 2: הגדרת סביבה
```bash
# 1. הגדרת CMS
echo "CMS_URL=https://192.168.1.24:433" >> .env
echo "CMS_USERNAME=admin" >> .env
echo "CMS_PASSWORD=admin123" >> .env
echo "CMS_TIMEOUT=30" >> .env
echo "CMS_VERIFY_SSL=false" >> .env

# 2. הגדרת API
echo "VITE_API_URL=http://192.168.1.30:8000" >> Frontend/.env
echo "VITE_CMS_MODE=remote" >> Frontend/.env
echo "VITE_CMS_URL=https://192.168.1.24:433" >> Frontend/.env
```

### שלב 3: הגדרת Docker (אם צריך)
```bash
# 1. בדיקת Docker
docker --version
docker-compose --version

# 2. הפעלת שירות
sudo systemctl start docker
sudo systemctl enable docker
```

### שלב 4: הפעלת המערכת
```bash
# 1. בניית והפעלה
docker-compose up -d --build

# 2. בדיקת סטטוס
docker-compose ps
```

### שלב 5: בדיקת חיבור CMS
```bash
# 1. בדיקת חיבור ל-CMS
curl -k -u "admin:admin123" https://192.168.1.24:433/system/status

# 2. בדיקת API
curl http://localhost:8000/meetings/active_calls
```

### שלב 6: הגדרת מסד נתונים
```bash
# 1. הפעלת Alembic
docker-compose exec fastapi_app alembic upgrade head

# 2. בדיקת טבלאות
docker-compose exec fastapi_app python -c "
from app.core.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)
"
```

## 🔧 קבצים להעתקה

### קבצי חובה:
- ✅ `Backend/app/service/cms.py` - קליינט CMS
- ✅ `Backend/app/service/meetingService.py` - שירות עם CMS
- ✅ `Backend/cms_config.py` - סקריפט הגדרה
- ✅ `Backend/.env` - משתני סביבה
- ✅ `Frontend/.env` - הגדרות פרונטאנד

### קבצי קונפיגורציה:
- ✅ `docker-compose.yml`
- ✅ `docker-compose.prod.yml`
- ✅ `Dockerfile.backend`
- ✅ `Dockerfile.prod`
- ✅ `Frontend/nginx.conf`

## 🎯 נקודות גישה

### API Endpoints:
- `GET http://192.168.1.30:8000/meetings/all_meetings`
- `GET http://192.168.1.30:8000/meetings/active_calls`
- `GET http://192.168.1.30:8000/meetings/call/{call_id}`
- `GET http://192.168.1.30:8000/meetings/call/{call_id}/participants`

### CMS Endpoints:
- `https://192.168.1.24:433/system/status`
- `https://192.168.1.24:433/coSpaces`
- `https://192.168.1.24:433/calls`

### פורטלים:
- Frontend: `http://192.168.1.30:3000`
- Backend API: `http://192.168.1.30:8000`
- CMS: `https://192.168.1.24:433`

## 🔍 בדיקות לאחר התקנה

### 1. בדיקת חיבור:
```bash
# בדיקת קונטיינרים
docker-compose ps

# בדיקת לוגים
docker-compose logs fastapi_app
docker-compose logs frontend
```

### 2. בדיקת API:
```bash
# בדיקת בריאות API
curl -X GET http://localhost:8000/health

# בדיקת CMS
curl -k -u "S@p180tech:admin123" https://192.168.1.24:433/system/status
```

### 3. בדיקת חיבור רשת:
```bash
# בדיקת פתיחות פורטים
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000
netstat -tulpn | grep :433

# בדיקת חומת אש
sudo ufw status
sudo ufw allow 8000
sudo ufw allow 3000
sudo ufw allow 433
```

## 🚨 פתרון תקלות

### בעיות נפוצות:
1. **חיבור CMS נכשל** - בדוק IP, סיסמה, חומת אש
2. **Docker לא עולה** - בדוק תלות קבצים, הרשאות
3. **API לא נגיש** - בדוק CORS, פורטים
4. **מסד נתונים לא מחובר** - בדוק DATABASE_URL

### פתרונות:
```bash
 # איפוס קונטיינרים
 docker-compose down -v
 
 # ניקוי תמונות
 docker system prune -a
 
 # בנייה מחדש
 docker-compose up -d --build
```

## 📞 תמיכה

### מידע חשוב:
- **שרת CMS:** 192.168.1.24:433
- **שרת אפליקציה:** 192.168.1.30
- **משתמש CMS:** admin
- **סיסמת CMS:** S@p180tech

### פקודות עזרה:
- בדיקת לוגים: `docker-compose logs [service_name]`
- הפעלה מחדש: `docker-compose restart [service_name]`
- גישה לקונטיינר: `docker-compose exec [service_name] bash`

## ✅ סיום התקנה

אחרי ביצוע כל השלבים, המערכת אמורה להיות מוכנה ומופעלת עם:
- ✅ חיבור ל-CMS
- ✅ API פעיל
- ✅ פרונטאנד מחובר
- ✅ מסד נתונים זמין

**המערכת מוכנה לשימוש!** 🎉
