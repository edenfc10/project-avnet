# ============================================================================
# CMS Mock Router - נתיבי API עבור CMS מדומה
# ============================================================================
# נתיבים:
#   GET    /cms_mock/meetings              - שליפת כל הישיבות או לפי סוג
#   GET    /cms_mock/meetings/{meetingId}  - שליפת ישיבה בודדת
#   POST   /cms_mock/meetings              - יצירת ישיבה חדשה
#   PUT    /cms_mock/meetings/{meetingId}/password - עדכון סיסמה
#   DELETE /cms_mock/meetings/{meetingId}  - מחיקת ישיבה
# ============================================================================

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.service.cms_mock import cms_mock_service
from logger import LoggerManager

cmsMockRouter = APIRouter()


# Pydantic models
class MeetingCreateRequest(BaseModel):
    meetingId: str
    name: Optional[str] = None
    type: str = "audio"
    group: Optional[str] = None
    cmsNode: Optional[str] = None


class MeetingPasswordUpdateRequest(BaseModel):
    password: str


class MeetingDeleteRequest(BaseModel):
    actor: Optional[dict] = None


# --- GET /cms_mock/meetings ---
@cmsMockRouter.get("/meetings", status_code=200)
async def get_cms_meetings(type: Optional[str] = Query(None, description="Filter by meeting type")):
    """מחזיר את כל הישיבות מה-MOCK CMS, או מסנן לפי סוג"""
    try:
        LoggerManager.get_logger().info("CMS Mock: Fetching meetings with type=%s", type)
        meetings = await cms_mock_service.get_meetings(meeting_type=type)
        return meetings
    except Exception as error:
        LoggerManager.get_logger().exception("CMS Mock: Failed to fetch meetings. Error: %s", str(error))
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- GET /cms_mock/meetings/{meetingId} ---
@cmsMockRouter.get("/meetings/{meetingId}", status_code=200)
async def get_cms_meeting_by_id(meetingId: str):
    """מחזיר ישיבה בודדת לפי meetingId"""
    try:
        LoggerManager.get_logger().info("CMS Mock: Fetching meeting with ID=%s", meetingId)
        meeting = await cms_mock_service.get_meeting_by_id(meeting_id=meetingId)
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        return meeting
    except HTTPException:
        raise
    except Exception as error:
        LoggerManager.get_logger().exception("CMS Mock: Failed to fetch meeting %s. Error: %s", meetingId, str(error))
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- POST /cms_mock/meetings ---
@cmsMockRouter.post("/meetings", status_code=201)
async def create_cms_meeting(meeting_data: MeetingCreateRequest):
    """יוצר ישיבה חדשה ב-MOCK CMS"""
    try:
        LoggerManager.get_logger().info("CMS Mock: Creating meeting with ID=%s", meeting_data.meetingId)
        
        meeting_dict = meeting_data.model_dump()
        meeting = await cms_mock_service.create_meeting(meeting_dict)
        
        if not meeting:
            raise HTTPException(status_code=400, detail="Failed to create meeting")
        
        return meeting
    except HTTPException:
        raise
    except Exception as error:
        LoggerManager.get_logger().exception("CMS Mock: Failed to create meeting. Error: %s", str(error))
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- PUT /cms_mock/meetings/{meetingId}/password ---
@cmsMockRouter.put("/meetings/{meetingId}/password", status_code=200)
async def update_cms_meeting_password(meetingId: str, request: MeetingPasswordUpdateRequest):
    """מעדכן סיסמת ישיבה ב-MOCK CMS"""
    try:
        LoggerManager.get_logger().info("CMS Mock: Updating password for meeting ID=%s", meetingId)
        
        meeting = await cms_mock_service.update_meeting_password(
            meeting_id=meetingId,
            new_password=request.password
        )
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        return meeting
    except HTTPException:
        raise
    except Exception as error:
        LoggerManager.get_logger().exception("CMS Mock: Failed to update password for meeting %s. Error: %s", meetingId, str(error))
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- DELETE /cms_mock/meetings/{meetingId} ---
@cmsMockRouter.delete("/meetings/{meetingId}", status_code=200)
async def delete_cms_meeting(meetingId: str, request: Optional[MeetingDeleteRequest] = None):
    """מוחק ישיבה מה-MOCK CMS"""
    try:
        LoggerManager.get_logger().info("CMS Mock: Deleting meeting with ID=%s", meetingId)
        
        actor = request.actor if request else None
        result = await cms_mock_service.delete_meeting(meeting_id=meetingId, actor=actor)
        
        return result
    except Exception as error:
        LoggerManager.get_logger().exception("CMS Mock: Failed to delete meeting %s. Error: %s", meetingId, str(error))
        raise HTTPException(status_code=500, detail="Internal Server Error")
