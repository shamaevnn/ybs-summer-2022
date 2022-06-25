from typing import Callable

from app.core.http import http_cli_close, http_cli_init
from app.db.events import close_db_connection, connect_to_db


def create_start_app_handler() -> Callable:  # type: ignore
    async def start_app() -> None:
        await connect_to_db()
        await http_cli_init()

    return start_app


def create_stop_app_handler() -> Callable:  # type: ignore
    async def close_app() -> None:
        await close_db_connection()
        await http_cli_close()

    return close_app
