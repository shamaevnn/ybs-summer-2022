from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.descriptions import API_description
from app.api.routes import api_router, statistic_api_router
from app.core.config import get_app_settings
from app.core.events import create_start_app_handler, create_stop_app_handler


def get_application() -> FastAPI:
    settings = get_app_settings()

    application = FastAPI(
        **dict(version="1.0.0", description=API_description, **settings.fastapi_kwargs)
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler(
        "startup",
        create_start_app_handler(),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(),
    )
    application.include_router(api_router)
    application.include_router(statistic_api_router)

    return application


app = get_application()
