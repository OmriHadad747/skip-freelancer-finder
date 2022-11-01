from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


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
    id: str
    job_category: JobCategoryEnum
    job_status: JobStatusEnum = JobStatusEnum.WAITING.value
    job_description: str
    job_price: str = None
    customer_email: str
    freelancer_email: str = None