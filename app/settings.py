from typing import Any
from pydantic import BaseSettings, BaseModel


class ProductionSettings(BaseSettings):
    environment: str = "production"
    debug: bool = False
    testing: bool = False

    firebase_sak_path: str

    crud_url: str

    class Config:
        env_prefix = "prod_"
        env_file = ".env"


class DevelopmentSettings(ProductionSettings):
    environment: str = "development"
    debug: bool = True
    testing: bool = False

    crud_url: str = "http://localhost:8000"

    class Config:
        env_prefix = "dev_"


class DockerDevelopmentSettings(DevelopmentSettings):
    crud_url: str = "http://skip-crud:8000"

    class Config:
        env_prefix = "docker_"


class AppSettings(BaseModel):
    setting: ProductionSettings | DevelopmentSettings | DockerDevelopmentSettings = None

    def init(
        self, env_settings: ProductionSettings | DevelopmentSettings | DockerDevelopmentSettings
    ):
        self.setting = env_settings()


app_settings = AppSettings()
