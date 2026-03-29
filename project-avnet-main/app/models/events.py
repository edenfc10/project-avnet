# ============================================================================
# SQLAlchemy Event Listeners - ×ž××–×™× ×™ ××™×¨×•×¢×™× (×ž×•×©×‘×ª ×›×¨×’×¢)
# ============================================================================
# ×§×•×‘×¥ ×–×” ×ž×›×™×œ event listeners ×©×œ SQLAlchemy ×©×ž×•×©×‘×ª×™× (commented out).
# ×”×¨×¢×™×•×Ÿ ×”×ž×§×•×¨×™: ×›×©×ž×•×¡×™×¤×™× ×¤×’×™×©×” ××• ×—×‘×¨ ×œ×ž×“×•×¨, ×”×ž×¢×¨×›×ª ×ª×™×¦×•×¨ ××•×˜×•×ž×˜×™×ª
# ××ª ×¨×©×•×ž×•×ª ×”×’×™×©×” ×‘×˜×‘×œ×ª member_group_access.
#
# ×›×¨×’×¢ ×”×”×¨×©××•×ª ×ž× ×•×”×œ×•×ª ×™×“× ×™×ª ×“×¨×š ×”-API (×”router/service/repo) -
# ×”××“×ž×™×Ÿ ×‘×•×—×¨ ×¨×ž×ª ×’×™×©×” ×‘×¢×ª ×”×•×¡×¤×ª ×—×‘×¨ ×œ×ž×“×•×¨.
# ============================================================================

from sqlalchemy import event
from sqlalchemy.orm import Session as SASession

from app.models.group import Group
from app.models.member_group_access import MemberGroupAccess


#@event.listens_for(Group.meetings, "append")
#def on_meeting_added_to_group(group, meeting, initiator):
 #   session = SASession.object_session(group)
  #  if not session:
   #     return
    #for member in group.members:
     #   exists = session.query(MemberGroupAccess).filter(
      #      MemberGroupAccess.member_uuid == member.UUID,
       #     MemberGroupAccess.group_uuid == group.UUID,
        #    MemberGroupAccess.access_level == meeting.accessLevel.value,
       # ).first()
        #if not exists:
         #   session.add(MemberGroupAccess(
          #      member_uuid=member.UUID,
           #     group_uuid=group.UUID,
            #    access_level=meeting.accessLevel.value,
           # ))


#@event.listens_for(Group.members, "append")
#def on_member_added_to_group(group, member, initiator):
#    session = SASession.object_session(group)
#    if not session:
#        return
#    for meeting in group.meetings:
#        exists = session.query(MemberGroupAccess).filter(
#            MemberGroupAccess.member_uuid == member.UUID,
#            MemberGroupAccess.group_uuid == group.UUID,
#            MemberGroupAccess.access_level == meeting.accessLevel.value,
#        ).first()
#        if not exists:
#            session.add(MemberGroupAccess(
#                member_uuid=member.UUID,
#                group_uuid=group.UUID,
#                access_level=meeting.accessLevel.value,
#            ))

