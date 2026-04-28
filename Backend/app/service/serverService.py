from fastapi import HTTPException
from app.models.meeting import AccessLevel
from app.repository.severRepo import ServerRepository
from app.schema.server import ServerInCreate, ServerInUpdate, ServerOutput
from app.config.cms_config import CMSConfig

class ServerService:
    def __init__(self, session):
        self.__serverRepository = ServerRepository(session=session)

    def _to_output(self, server) -> ServerOutput:
        return ServerOutput.model_validate(server)

    def create_server(self, server_data: ServerInCreate) -> ServerOutput:
        return self._to_output(self.__serverRepository.create_server(server_data=server_data))

    def get_all_servers(self, access_level: AccessLevel | None = None) -> list[ServerOutput]:
        return [
            self._to_output(server)
            for server in self.__serverRepository.get_all_servers(access_level=access_level)
        ]

    def delete_server(self, server_uuid: str) -> None:
        success = self.__serverRepository.delete_server(server_uuid=server_uuid)
        if not success:
            raise HTTPException(status_code=404, detail="Server not found")

    def update_server(self, server_uuid: str, server_data: ServerInUpdate) -> ServerOutput:
        updated_server = self.__serverRepository.update_server(server_uuid=server_uuid, server_data=server_data)
        if updated_server:
            return self._to_output(updated_server)
        raise HTTPException(status_code=404, detail="Server not found")
    
    def get_cms_servers_status(self) -> dict:
        """בדיקת סטטוס כל שרתי ה-CMS המוגדרים"""
        status = {}
        for server_name in CMSConfig.get_all_cms_servers():
            try:
                is_connected = CMSConfig.test_connection(server_name)
                server_config = CMSConfig.get_cms_server(server_name)
                status[server_name] = {
                    "connected": is_connected,
                    "host": server_config["base_url"],
                    "status": "online" if is_connected else "offline"
                }
            except Exception as e:
                status[server_name] = {
                    "connected": False,
                    "host": f"Error: {str(e)}",
                    "status": "error"
                }
        return status