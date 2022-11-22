from skip_common_lib.config import BaseConfig
from flask import Flask


def create_app(app_config: BaseConfig) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config)

    with app.app_context():
        from skip_common_lib.database import mongo
        mongo.init_app(app)

        import firebase_admin
        from skip_common_lib.extensions import jwt, firebase_admin_creds
        # from app.extensions import firebase_admin, firebase_admin_creds
        firebase_admin.initialize_app(firebase_admin_creds)
        jwt.init_app(app)

        from app import routes
        app.register_blueprint(routes.freelancer_finder_bp)

        return app
