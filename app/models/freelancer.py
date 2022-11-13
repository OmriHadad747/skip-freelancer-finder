from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import Field, BaseModel, constr, conlist
from flask import current_app
from app.models import job as job_model


class FreelancerCategoryEnum(Enum):
    GARAGE      = 0
    LOCKSMITH   = 1


class FreelancerStatusEnum(Enum):
    AVAILABLE = 0
    BUSY      = 1  


class Freelancer(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    password: str 
    email: str
    phone: str
    county: str
    tmp_county: Optional[str]
    tmp_county_date: Optional[datetime]
    category: List[FreelancerCategoryEnum] = []
    rating: float = 1.0
    job_history: List[job_model.Job] = []
    current_status: FreelancerStatusEnum = FreelancerStatusEnum.AVAILABLE.value
    current_location: Optional[conlist(item_type=float, min_items=2, max_items=2)]
    current_location_date: Optional[datetime]
    registration_token: str


class FreelancerUpdate(BaseModel):
    updated_at: datetime = Field(default_factory=datetime.now)
    password: str
    email: Optional[str]
    phone: Optional[str]
    tmp_county: Optional[str]
    tmp_county_date: datetime = None
    current_status: Optional[FreelancerStatusEnum]
    current_location: Optional[conlist(item_type=float, min_items=2, max_items=2)]
    current_location_date: Optional[datetime]
    registration_token: Optional[str]