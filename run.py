from app import create_app
from skip_common_lib import config


if __name__ == "__main__":
    app = create_app(config.DevConfig)
    app.run(host="0.0.0.0", port=4999)
