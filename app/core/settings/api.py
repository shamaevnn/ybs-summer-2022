import logging
from typing import Any, Dict, List, Tuple, Union

from pydantic import PostgresDsn

from app.core.settings.base import BaseAppSettings


class AppSettings(BaseAppSettings):

    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "Mega Market via FASTApi"

    database_url: Union[str, PostgresDsn]
    max_connection_count: int = 10
    min_connection_count: int = 10

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
        }
