import pydantic as pyd

from fastapi import FastAPI
from logging.config import dictConfig


def create_app(settings: pyd.BaseSettings) -> FastAPI:
    app = FastAPI()

    # init settings
    from skip_common_lib.settings import app_settings
    app_settings.init(settings)

    # init logging configuration
    from skip_common_lib.logging import LogConfig
    dictConfig(LogConfig(LOGGER_NAME="skip-freelancerfinder-service").dict())

    # init clients
    from app import clients

    # init routes
    from app.routes import finder
    app.include_router(finder.api)

    return app
