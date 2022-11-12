from app import config
from flask import Flask


def create_app(app_config: config.BaseConfig) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config)

    with app.app_context():
        # init flask-extensions
        from app.extensions import mongo, firebase_admin, firebase_admin_creds
        mongo.init_app(app)
        firebase_admin.initialize_app(firebase_admin_creds)

        from app import routes
        app.register_blueprint(routes.freelancer_finder_bp)

        return app