import pydantic as pyd

from typing import Any, Dict
from datetime import datetime
from enum import Enum
from bson import ObjectId

from app.schemas import CustomBaseModel


class JobCategoryEnum(Enum):
    GARAGE_DOOR = 0
    LOCK_SMITH = 1
    MOVING = 2


class JobStatusEnum(Enum):
    FREELANCER_FINDING = "freelancer-finding"
    FREELANCER_FOUND = "freelancer-found"
    FREELANCER_CANCELED = "freelancer-canceled"
    CUSTOMER_CANCELD = "customer-canceld"
    APPROVED = "customer-approved"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class JobQuotation(CustomBaseModel):
    description: str
    estimated_job_duration: str
    price: str

    def quotation_to_str(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "estimated_job_duration": self.estimated_job_duration,
            "price": self.price,
        }


class Job(CustomBaseModel):
    created_at: datetime = pyd.Field(default_factory=datetime.now)
    id: str = pyd.Field(alias="_id", default_factory=ObjectId)
    category: JobCategoryEnum
    status: JobStatusEnum = JobStatusEnum.FREELANCER_FINDING.value
    description: str
    location: list[float] = pyd.Field(min_items=2, max_items=2)
    quotation: JobQuotation = None
    price: str = None
    customer_email: str
    customer_phone: str
    customer_address: str
    customer_county: str
    freelancer_email: str = None
    freelancer_phone: str = None

    @pyd.validator("id", pre=True)
    def convert_id_to_str(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    def job_to_str(
        self, customer_part: bool = True, freelancer_part: bool = False
    ) -> Dict[str, Any]:
        job_data = {
            "job_id": str(self.id),
            "job_category": str(self.category),
            "job_description": self.description,
            "job_lon": str(self.location[0]),
            "job_lat": str(self.location[1]),
        }

        if customer_part:
            job_data.update(
                {
                    "customer_email": self.customer_email,
                    "customer_phone": self.customer_phone,
                    "customer_address": self.customer_address,
                    "customer_county": self.customer_county,
                }
            )

        if freelancer_part:
            job_data.update(
                {
                    "freelancer_email": self.freelancer_email,
                    "freelancer_phone": self.freelancer_phone,
                }
            )

        return job_data


class JobUpdate(CustomBaseModel):
    status: JobStatusEnum = None
    quotation: JobQuotation = None
    price: str = None
    freelancer_email: str = None
    freelancer_phone: str = None
