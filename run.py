import uvicorn

from app import create_app
from app import settings


app = create_app(settings.DevelopmentSettings)


if __name__ == "__main__":
    uvicorn.run(app="run:app", host="localhost", port=8001, reload=True)
