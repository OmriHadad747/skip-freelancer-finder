import firebase_admin

from firebase_admin import credentials

from app.settings import app_settings as s


firebase_admin_creds = credentials.Certificate(s.setting.firebase_sak_path)
firebase_admin.initialize_app(firebase_admin_creds)
