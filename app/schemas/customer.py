import pydantic as pyd

from datetime import datetime
from bson import ObjectId

from app.schemas import CustomBaseModel
from app.schemas.job import Job


class Customer(CustomBaseModel):
    created_at: datetime = pyd.Field(default_factory=datetime.now)
    _id: int = ObjectId()
    password: str
    email: str
    phone: str
    address: str
    county: str
    rating: float = 1.0
    job_history: list[Job] = []
    location: list[float] = pyd.Field(min_items=2, max_items=2)
    registration_token: str


class CustomerUpdate(CustomBaseModel):
    updated_at: datetime = pyd.Field(default_factory=datetime.now)
    password: str = None
    email: str = None
    phone: str = None
    address: str = None
    county: str = None
    location: list[float] = pyd.Field(min_items=2, max_items=2, default=None)
    registration_token: str = None
