from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from flask_pymongo import ObjectId


class JobCategoryEnum(Enum):
    GARAGE_DOOR = 0
    LOCK_SMITH = 1


class JobStatusEnum(Enum):
    WAITING     = 0
    CANCELED    = 1
    IN_PROGRESS = 2
    DONE        = 3


class Job(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    id: int = Field(alias="_id", default_factory=ObjectId)
    job_category: JobCategoryEnum   # TODO change to list of categories in the future
    job_status: JobStatusEnum = JobStatusEnum.WAITING.value
    job_description: str
    job_price: str = None
    customer_email: str
    customer_phone: str
    customer_address: str
    customer_county: str
    customer_lon: float
    customer_lat: float
    freelancer_email: str = None
    freelancer_phone: str = None