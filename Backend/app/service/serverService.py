from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.meeting import AccessLevel
from app.models.server import Server
from app.repository.severRepo import ServerRepository
from app.schema.server import (
    ServerInCreate, ServerInUpdate, ServerOutput, 
    ConnectionTestResult, ServerSetPrimary, ServerStats
)
from app.service.cms import CMS
from datetime import datetime
import time
from logger import LoggerManager

class ServerService:
    def __init__(self, session: Session):
        self.__serverRepository = ServerRepository(session=session)
        self.logger = LoggerManager.get_logger()

    def _to_output(self, server: Server) -> ServerOutput:
        """המרת מודל Server ל-Pydantic output"""
        return ServerOutput(
            UUID=server.UUID,
            server_name=server.server_name,
            ip_address=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            accessLevel=server.accessLevel,
            is_active=server.is_active,
            is_primary=server.is_primary,
            connection_status=server.connection_status,
            last_connection_test=server.last_connection_test,
            connection_error=server.connection_error,
            server_version=server.server_version,
            system_info=server.system_info,
            created_at=server.created_at,
            updated_at=server.updated_at
        )

    def create_server(self, server_data: ServerInCreate) -> ServerOutput:
        """יצירת שרת CMS חדש עם בדיקת חיבור"""
        try:
            # בדיקה אם כבר יש שרת ראשי אם מנסים להגדיר חדש
            if server_data.is_primary:
                existing_primary = self.get_primary_server()
                if existing_primary:
                    raise HTTPException(
                        status_code=400, 
                        detail="כבר קיים שרת ראשי. יש לבטל את השרת הראשי הקיים קודם."
                    )
            
            # בדיקת חיבור לפני יצירה
            connection_result = self._test_connection_direct(
                server_data.ip_address, server_data.port, 
                server_data.username, server_data.password
            )
            
            if not connection_result.success:
                raise HTTPException(
                    status_code=400,
                    detail=f"בדיקת חיבור נכשלה: {connection_result.message}"
                )
            
            # יצירת השרת עם סטטוס מחובר
            server_dict = server_data.dict()
            server_dict['connection_status'] = 'connected'
            server_dict['server_version'] = connection_result.server_version
            server_dict['system_info'] = connection_result.system_info
            server_dict['last_connection_test'] = datetime.utcnow()
            
            server = self.__serverRepository.create_server(server_data=server_dict)
            
            self.logger.info(
                "CMS server created successfully: %s (%s:%s)",
                server.server_name, server.ip_address, server.port
            )
            
            return self._to_output(server)
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("Failed to create CMS server: %s", str(e))
            raise HTTPException(status_code=500, detail="שגיאה ביצירת שרת CMS")

    def get_all_servers(self, access_level: AccessLevel | None = None) -> list[ServerOutput]:
        """קבלת כל השרתים"""
        return [
            self._to_output(server)
            for server in self.__serverRepository.get_all_servers(access_level=access_level)
        ]

    def get_active_servers(self) -> List[ServerOutput]:
        """קבלת שרתים פעילים ומחוברים בלבד"""
        servers = self.__serverRepository.get_all_servers()
        return [
            self._to_output(server) 
            for server in servers 
            if server.is_active and server.connection_status == 'connected'
        ]

    def get_primary_server(self) -> Optional[ServerOutput]:
        """קבלת השרת הראשי"""
        servers = self.__serverRepository.get_all_servers()
        primary_server = next((s for s in servers if s.is_primary), None)
        return self._to_output(primary_server) if primary_server else None

    def delete_server(self, server_uuid: str) -> None:
        """מחיקת שרת (soft delete)"""
        try:
            server = self.__serverRepository.get_server_by_uuid(server_uuid)
            if not server:
                raise HTTPException(status_code=404, detail="Server not found")
            
            success = self.__serverRepository.delete_server(server_uuid=server_uuid)
            if success:
                self.logger.info("CMS server deleted: %s", server.server_name)
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("Failed to delete CMS server %s: %s", server_uuid, str(e))
            raise HTTPException(status_code=500, detail="שגיאה במחיקת שרת CMS")

    def update_server(self, server_uuid: str, server_data: ServerInUpdate) -> ServerOutput:
        """עדכון שרת CMS"""
        try:
            server = self.__serverRepository.get_server_by_uuid(server_uuid)
            if not server:
                raise HTTPException(status_code=404, detail="Server not found")
            
            update_dict = server_data.dict(exclude_unset=True)
            
            # אם מעדכנים פרטי התחברות - בדוק חיבור מחדש
            if any(key in update_dict for key in ['ip_address', 'port', 'username', 'password']):
                host = update_dict.get('ip_address', server.ip_address)
                port = update_dict.get('port', server.port)
                username = update_dict.get('username', server.username)
                password = update_dict.get('password', server.password)
                
                connection_result = self._test_connection_direct(host, port, username, password)
                
                if not connection_result.success:
                    raise HTTPException(
                        status_code=400,
                        detail=f"בדיקת חיבור נכשלה: {connection_result.message}"
                    )
                
                update_dict.update({
                    'connection_status': 'connected',
                    'server_version': connection_result.server_version,
                    'system_info': connection_result.system_info,
                    'last_connection_test': datetime.utcnow(),
                    'connection_error': None
                })
            
            # אם מגדירים כראשי
            if update_dict.get('is_primary') == True:
                self.set_primary_server(server_uuid)
                update_dict.pop('is_primary')  # כבר טופל
            
            updated_server = self.__serverRepository.update_server(server_uuid=server_uuid, server_data=update_dict)
            
            if updated_server:
                self.logger.info("CMS server updated: %s", updated_server.server_name)
                return self._to_output(updated_server)
            
            raise HTTPException(status_code=404, detail="Server not found")
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("Failed to update CMS server %s: %s", server_uuid, str(e))
            raise HTTPException(status_code=500, detail="שגיאה בעדכון שרת CMS")

    def test_connection(self, server_uuid: str) -> ConnectionTestResult:
        """בדיקת חיבור לשרת קיים"""
        try:
            server = self.__serverRepository.get_server_by_uuid(server_uuid)
            if not server:
                raise HTTPException(status_code=404, detail="Server not found")
            
            result = self._test_connection_direct(
                server.ip_address, server.port, server.username, server.password
            )
            
            # עדכון סטטוס במסד נתונים
            status = 'connected' if result.success else 'error'
            error = None if result.success else result.message
            
            self.__serverRepository.update_connection_status(server_uuid, status, error)
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("Failed to test connection for server %s: %s", server_uuid, str(e))
            raise HTTPException(status_code=500, detail="שגיאה בבדיקת חיבור")

    def set_primary_server(self, server_uuid: str) -> bool:
        """הגדרת שרת כראשי"""
        try:
            server = self.__serverRepository.get_server_by_uuid(server_uuid)
            if not server:
                raise HTTPException(status_code=404, detail="Server not found")
            
            if server.connection_status != 'connected':
                raise HTTPException(
                    status_code=400, 
                    detail="ניתן להגדיר כראשי רק שרת מחובר"
                )
            
            success = self.__serverRepository.set_primary_server(server_uuid)
            
            if success:
                self.logger.info("CMS server set as primary: %s", server.server_name)
            
            return success
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("Failed to set primary server %s: %s", server_uuid, str(e))
            raise HTTPException(status_code=500, detail="שגיאה בהגדרת שרת ראשי")

    def get_server_stats(self) -> ServerStats:
        """קבלת סטטיסטיקת שרתים"""
        servers = self.__serverRepository.get_all_servers()
        
        total = len([s for s in servers if s.is_active])
        connected = len([s for s in servers if s.is_active and s.connection_status == 'connected'])
        disconnected = len([s for s in servers if s.is_active and s.connection_status == 'disconnected'])
        error = len([s for s in servers if s.is_active and s.connection_status == 'error'])
        
        return ServerStats(
            total=total,
            connected=connected,
            disconnected=disconnected,
            error=error
        )

    def get_cms_client_for_server(self, server_uuid: str = None, access_level: AccessLevel = None) -> Optional[CMS]:
        """קבלת CMS client עבור שרת ספציפי"""
        try:
            if server_uuid:
                server = self.__serverRepository.get_server_by_uuid(server_uuid)
            elif access_level:
                # חיפוש שרת לפי סוג (audio/video/blast_dial)
                servers = self.__serverRepository.get_all_servers()
                server = next((s for s in servers if s.accessLevel == access_level and s.is_active and s.connection_status == 'connected'), None)
            else:
                # שרת ראשי כברירת מחדל
                servers = self.__serverRepository.get_all_servers()
                server = next((s for s in servers if s.is_primary and s.is_active and s.connection_status == 'connected'), None)
            
            if not server:
                return None
            
            # יצירת CMS client עם פרטי השרת
            return CMS(
                host=server.ip_address,
                port=server.port,
                username=server.username,
                password=server.password
            )
            
        except Exception as e:
            self.logger.error("Failed to get CMS client: %s", str(e))
            return None

    def _test_connection_direct(self, host: str, port: int, username: str, password: str) -> ConnectionTestResult:
        """בדיקת חיבור ישירה ל-CMS"""
        try:
            start_time = time.time()
            
            cms = CMS(host=host, port=port, username=username, password=password)
            system_info = cms.get_system_info()
            
            response_time = (time.time() - start_time) * 1000  # ב-milliseconds
            
            return ConnectionTestResult(
                success=True,
                message="חיבור הצליח",
                server_version=system_info.get('version', 'Unknown'),
                system_info=str(system_info),
                response_time_ms=response_time
            )
            
        except Exception as e:
            return ConnectionTestResult(
                success=False,
                message=f"שגיאת חיבור: {str(e)}",
                response_time_ms=None
            )