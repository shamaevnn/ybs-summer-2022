from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseSettings, PostgresDsn


class AppEnvTypes(Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.prod

    debug: bool = False

    database_url: Union[str, PostgresDsn]
    max_connection_count: int = 10
    min_connection_count: int = 10

    @property
    def db_options(self) -> Dict[str, Any]:
        if "postgres" in self.database_url:
            options = {
                "min_size": self.min_connection_count,
                "max_size": self.max_connection_count,
            }
        elif "sqlite" in self.database_url:
            options = {}
        else:
            raise ValueError(f"Unknown db engine = {self.database_url}")
        return options

    @property
    def render_as_batch(self) -> bool:
        if "sqlite" in self.database_url:
            return True
        return False

    class Config:
        env_file = ".env"
