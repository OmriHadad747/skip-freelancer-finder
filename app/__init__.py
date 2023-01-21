import pydantic as pyd

from fastapi import FastAPI
from logging.config import dictConfig


def create_app(settings: pyd.BaseSettings) -> FastAPI:
    app = FastAPI()

    # init settings
    from app.settings import app_settings
    app_settings.init(settings)

    # init logging
    from skip_common_lib.logging import LogConfig
    dictConfig(LogConfig().dict())

    # init firebase sdk
    from app import clients 

    # init routes
    from app.routes import finder, quotation
    app.include_router(finder.api, tags=["Finder"])
    app.include_router(quotation.api, tags=["Quotation"])

    return app
