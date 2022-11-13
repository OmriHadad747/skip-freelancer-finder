import firebase_admin

from flask_pymongo import PyMongo as FlaskPymongo
from firebase_admin import credentials
from flask import current_app as app


mongo = FlaskPymongo()


firebase_admin_creds = credentials.Certificate(app.config["FIREBASE_SERVICE_ACCOUNT"])