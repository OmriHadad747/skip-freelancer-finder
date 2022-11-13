from app import create_app
from app import config


if __name__ == "__main__":
    app = create_app(config.DevConfig)
    app.run(host="localhost", port=4999, debug=True)