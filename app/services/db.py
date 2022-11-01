from typing import Optional, Any
from flask_pymongo import PyMongo as FlaskPymongo
from flask_pymongo import wrappers
from flask import current_app, g
from werkzeug.local import LocalProxy
from app.models import freelancer as freelancer_model


def get_dbs() -> wrappers.Collection:
    if "database" not in g:
        g.database = FlaskPymongo(current_app, uuidRepresentation="standard")
    return g.database.db

db: wrappers.Collection = LocalProxy(get_dbs)
_freelancers = current_app.config["FREELANCER_COLLECTION"]


class FreelancerDatabase:

    @classmethod
    def find(cls, county: str, lon: float, lat: float) -> Optional[Any]:
        freelancers = db[_freelancers].aggregate([
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "spherical": True,
                    "query": {
                        "current_status": freelancer_model.FreelancerStatusEnum.AVAILABLE.value,
                        "county": county
                    },
                    "distanceField": "distance"
                }
            }
        ])
        return freelancers


        