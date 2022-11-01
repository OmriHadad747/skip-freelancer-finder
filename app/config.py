from os import environ
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = environ.get("SECRET_KEY")


class ProdConfig(BaseConfig):
    # General flask's configuration
    ENV = "production"
    FLASK_ENV = "production"
    TESTING = False
    DEBUG = False
    

class DevConfig(BaseConfig):
    # General flask's configuration
    ENV = "development"
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = False

    # MongoDB
    MONGO_URI = environ.get("MONGO_URI_DEV")
    FREELANCER_COLLECTION = environ.get("FREELANCER_COLLECTION_DEV")
    JOB_COLLECTION = environ.get("JOB_COLLECTION_DEV")

    # crud service
    CRUD_HOST = "localhost:5000"


class TestConfig(BaseConfig):
    # General flask's configuration
    ENV = "testing"
    FLASK_ENV = "testing"
    DEBUG = False
    TESTING = True

    # MongoDB
    MONGO_URI = environ.get("MONGO_URI_TEST")
    FREELANCER_COLLECTION = environ.get("FREELANCERS_COLLECTION_TEST")
    JOB_COLLECTION = environ.get("JOB_COLLECTION_TEST")