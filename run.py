from app import create_app
from app import config


if __name__ == "__main__":
    app = create_app(config.LocalDockerizingConfig)
    app.run(host="0.0.0.0", port=4999)
