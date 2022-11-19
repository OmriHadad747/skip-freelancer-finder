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

    # MongoDB
    MONGO_URI = environ.get("MONGO_URI_PROD")
    FREELANCER_COLLECTION = environ.get("FREELANCER_COLLECTION_PROD")
    JOB_COLLECTION = environ.get("JOB_COLLECTION_PROD")

    # crud service
    CRUD_HOST = "N/A"

    # FIREBASE
    FIREBASE_SERVICE_ACCOUNT = environ.get("FIREBASE_SERVICE_ACCOUNT_PROD")


class LocalDockerizingConfig(BaseConfig):
    # General flask's configuration
    ENV = "development"
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = False

    # MongoDB
    MONGO_URI = environ.get("MONGO_URI_DEV_DOCKER")
    CUSTOMER_COLLECTION = environ.get("CUSTOMER_COLLECTION_DEV_DOCKER")
    FREELANCER_COLLECTION = environ.get("FREELANCER_COLLECTION_DEV_DOCKER")
    JOB_COLLECTION = environ.get("JOB_COLLECTION_DEV_DOCKER")

    # crud service
    CRUD_HOST = "skip-crud-container:5000"

    # FIREBASE
    FIREBASE_SERVICE_ACCOUNT = environ.get("FIREBASE_SERVICE_ACCOUNT_DEV")


class DevConfig(BaseConfig):
    # General flask's configuration
    ENV = "development"
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = False

    # MongoDB
    MONGO_URI = environ.get("MONGO_URI_DEV")
    CUSTOMER_COLLECTION = environ.get("CUSTOMER_COLLECTION_DEV")
    FREELANCER_COLLECTION = environ.get("FREELANCER_COLLECTION_DEV")
    JOB_COLLECTION = environ.get("JOB_COLLECTION_DEV")

    # crud service
    CRUD_HOST = "localhost:5000"

    # FIREBASE
    FIREBASE_SERVICE_ACCOUNT = environ.get("FIREBASE_SERVICE_ACCOUNT_DEV")


class TestConfig(BaseConfig):
    # General flask's configuration
    ENV = "testing"
    FLASK_ENV = "testing"
    DEBUG = False
    TESTING = True

    # MongoDB
    MONGO_URI = environ.get("MONGO_URI_TEST")
    CUSTOMER_COLLECTION = environ.get("CUSTOMER_COLLECTION_TEST")
    FREELANCER_COLLECTION = environ.get("FREELANCERS_COLLECTION_TEST")
    JOB_COLLECTION = environ.get("JOB_COLLECTION_TEST")
