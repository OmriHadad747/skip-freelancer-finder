import firebase_admin

from firebase_admin import credentials
from flask import current_app as app


firebase_admin_creds = credentials.Certificate(app.config["FIREBASE_SERVICE_ACCOUNT"])