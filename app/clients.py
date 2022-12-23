import firebase_admin

from firebase_admin import credentials

from skip_common_lib.settings import app_settings as s


firebase_admin_creds = credentials.Certificate(s.setting.firebase_sak)
firebase_admin.initialize_app(firebase_admin_creds)
