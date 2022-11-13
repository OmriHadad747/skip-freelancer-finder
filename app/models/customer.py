from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import Field, BaseModel, constr
from flask import current_app
from app.models import job as job_model


class Customer(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    password: str
    email: str
    phone: str
    address: str
    county: str
    rating: float = 1.0
    job_history: List[job_model.Job] = []
    lon: Optional[float]
    lat: Optional[float]


# class CustomerUpdate(BaseModel):
#     updated_at: datetime = Field(default_factory=datetime.now)
#     password: Optional[constr(min_length=current_app.config["PASSWORD_MIN_LENGTH"], max_length=10)]
#     email: Optional[str]
#     phone: Optional[str]
#     address: Optional[str]
#     county: Optional[str]