# ============================================================================
# CMS Mock Service - שירות CMS מדומה
# ============================================================================
# קובץ זה מדמה שרת CMS חיצוני עם נתוני ישיבות.
# משמש לפיתוח ובדיקות ללא צורך בשרת CMS אמיתי.
# ============================================================================

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# נתוני CMS מדומים
CMS_MEETINGS = [
    {
        "id": "cms-1001",
        "meetingId": "891245",
        "name": "Command Audio Bridge",
        "type": "audio",
        "group": "Operations",
        "accessLevel": "audio",
        "status": "active",
        "participantsCount": 12,
        "duration": 34,
        "lastUsedAt": "2026-03-22T08:40:00Z",
        "password": "AUDIO-7781",
        "passwordMasked": "******",
        "cmsNode": "CMS-DC-1",
    },
    {
        "id": "cms-1002",
        "meetingId": "891246",
        "name": "Daily Ops Audio",
        "type": "audio",
        "group": "NOC",
        "accessLevel": "audio",
        "status": "idle",
        "participantsCount": 0,
        "duration": 0,
        "lastUsedAt": "2026-04-05T16:20:00Z",
        "password": "AUDIO-3394",
        "passwordMasked": "******",
        "cmsNode": "CMS-DC-2",
    },
    {
        "id": "cms-2001",
        "meetingId": "771110",
        "name": "Leadership Video Room",
        "type": "video",
        "group": "Management",
        "accessLevel": "video",
        "status": "active",
        "participantsCount": 7,
        "duration": 52,
        "lastUsedAt": "2026-04-05T09:05:00Z",
        "password": "VIDEO-2288",
        "passwordMasked": "******",
        "cmsNode": "CMS-DC-1",
    },
    {
        "id": "cms-2002",
        "meetingId": "771111",
        "name": "Training Video Hall",
        "type": "video",
        "group": "HR",
        "accessLevel": "video",
        "status": "scheduled",
        "participantsCount": 0,
        "duration": 0,
        "lastUsedAt": "2026-04-05T12:35:00Z",
        "password": "VIDEO-9915",
        "passwordMasked": "******",
        "cmsNode": "CMS-DC-3",
    },
    {
        "id": "cms-3001",
        "meetingId": "551900",
        "name": "Mass Notification Dialout",
        "type": "blast_dial",
        "group": "Emergency",
        "accessLevel": "blast_dial",
        "status": "active",
        "participantsCount": 24,
        "duration": 9,
        "lastUsedAt": "2026-04-05T07:55:00Z",
        "password": "BLAST-1044",
        "passwordMasked": "******",
        "cmsNode": "CMS-DC-2",
    },
    {
        "id": "cms-3002",
        "meetingId": "551901",
        "name": "Legacy Blast Group",
        "type": "blast_dial",
        "group": "NOT IN USE",
        "accessLevel": "blast_dial",
        "status": "not_in_use",
        "participantsCount": 0,
        "duration": 0,
        "lastUsedAt": "2026-04-05T05:10:00Z",
        "password": "BLAST-0000",
        "passwordMasked": "******",
        "cmsNode": "CMS-DC-3",
    },
]


class CMSMockService:
    """שירות CMS מדומה לפיתוח"""
    
    def __init__(self):
        self.meetings = CMS_MEETINGS.copy()
    
    async def _delay(self, ms: int = 300):
        """מדמה השהיה של קריאת רשת"""
        await asyncio.sleep(ms / 1000)
    
    async def get_meetings(self, meeting_type: Optional[str] = None) -> List[Dict]:
        """מחזיר את כל הישיבות, או מסנן לפי סוג"""
        await self._delay(300)
        
        if not meeting_type:
            return self.meetings
        
        return [m for m in self.meetings if m.get("type") == meeting_type]
    
    async def get_meeting_by_id(self, meeting_id: str) -> Optional[Dict]:
        """מחזיר ישיבה בודדת לפי meetingId"""
        await self._delay(300)
        
        for meeting in self.meetings:
            if meeting.get("meetingId") == meeting_id:
                return meeting
        
        return None
    
    async def create_meeting(self, meeting_data: Dict) -> Optional[Dict]:
        """יוצר ישיבה חדשה ב-CMS"""
        await self._delay(300)
        
        meeting_id = str(meeting_data.get("meetingId", "")).strip()
        if not meeting_id:
            return None
        
        # בדוק אם כבר קיימת
        for meeting in self.meetings:
            if meeting.get("meetingId") == meeting_id:
                return meeting
        
        meeting_type = meeting_data.get("type", "audio")
        password_prefix = (
            "VIDEO" if meeting_type == "video" 
            else "BLAST" if meeting_type == "blast_dial" 
            else "AUDIO"
        )
        
        import random
        random_suffix = random.randint(1000, 9999)
        password = f"{password_prefix}-{random_suffix}"
        
        # מצא את ה-ID הבא
        max_id = 0
        for meeting in self.meetings:
            id_str = meeting.get("id", "").replace("cms-", "")
            try:
                id_num = int(id_str)
                max_id = max(max_id, id_num)
            except ValueError:
                pass
        
        next_id = max_id + 1
        
        created = {
            "id": f"cms-{next_id}",
            "meetingId": meeting_id,
            "name": meeting_data.get("name", f"Meeting {meeting_id}"),
            "type": meeting_type,
            "group": meeting_data.get("group", "Unassigned"),
            "accessLevel": meeting_type,
            "status": "idle",
            "participantsCount": 0,
            "duration": 0,
            "lastUsedAt": datetime.utcnow().isoformat() + "Z",
            "password": password,
            "passwordMasked": "******",
            "cmsNode": meeting_data.get("cmsNode", "CMS-LOCAL-1"),
        }
        
        self.meetings.insert(0, created)
        return created
    
    async def update_meeting_password(self, meeting_id: str, new_password: str) -> Optional[Dict]:
        """מעדכן סיסמת ישיבה ב-CMS"""
        await self._delay(300)
        
        for meeting in self.meetings:
            if meeting.get("meetingId") == meeting_id:
                meeting["password"] = new_password
                meeting["passwordMasked"] = "******" if new_password else "-"
                meeting["lastUsedAt"] = datetime.utcnow().isoformat() + "Z"
                return meeting
        
        return None
    
    async def delete_meeting(self, meeting_id: str, actor: Optional[Dict] = None) -> Dict:
        """מוחק ישיבה מה-CMS"""
        await self._delay(300)
        
        for i, meeting in enumerate(self.meetings):
            if meeting.get("meetingId") == meeting_id:
                role = actor.get("role", "") if actor else ""
                
                # בדוק הרשאות
                if role not in ["super_admin", "admin"]:
                    return {"deleted": False, "reason": "forbidden"}
                
                if role == "admin":
                    owned_groups = [g.lower().strip() for g in (actor.get("ownedGroups") or [])]
                    meeting_group = meeting.get("group", "").lower().strip()
                    
                    if meeting_group not in owned_groups:
                        return {"deleted": False, "reason": "forbidden"}
                
                self.meetings.pop(i)
                return {"deleted": True, "reason": "ok"}
        
        return {"deleted": False, "reason": "not_found"}


# מופע גלובלי של השירות
cms_mock_service = CMSMockService()
