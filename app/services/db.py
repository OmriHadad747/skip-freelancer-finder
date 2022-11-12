from typing import Optional, Any
from pymongo import command_cursor
from flask_pymongo import PyMongo as FlaskPymongo
from flask_pymongo import wrappers
from flask import current_app, g
from werkzeug.local import LocalProxy
from bson import ObjectId
from app.models import freelancer as freelancer_model
from app.models import job as job_moedl


def get_dbs() -> wrappers.Collection:
    if "database" not in g:
        g.database = FlaskPymongo(current_app, uuidRepresentation="standard")
    return g.database.db

db: wrappers.Collection = LocalProxy(get_dbs)
_freelancers = current_app.config["FREELANCER_COLLECTION"]
_jobs = current_app.config["JOB_COLLECTION"]


class JobDatabase:

    @classmethod
    def add_job(cls, job: job_moedl.Job) -> Optional[bool]:
        # TODO log here - f"saving job {job.id} to database"
        result = db[_jobs].insert_one(job.dict())
        return result.acknowledged

    
    @classmethod
    def get_job_by_id(cls, id: str) -> job_moedl.Job:
        job = db[_jobs].find_one({"_id": ObjectId(id)})
        return job



class FreelancerDatabase:

    @classmethod
    def find(cls, job: job_moedl.Job) ->  command_cursor.CommandCursor:
        # TODO write docstring
        # TODO log here
        freelancers = db[_freelancers].aggregate([
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [job.customer_lon, job.customer_lat]
                    },
                    "spherical": True,
                    "query": {
                        "current_status": freelancer_model.FreelancerStatusEnum.AVAILABLE.value,
                        "county": job.customer_county
                    },
                    "distanceField": "distance"
                }
            }
        ])
        # TODO log here
        yield freelancers