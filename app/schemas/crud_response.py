from app.schemas import CustomBaseModel
from app.schemas.freelancer import Freelancer
from app.schemas.job import Job
from app.schemas.customer import Customer


class AvailableFreelancers(CustomBaseModel):
    available_freelancers: list[Freelancer]


class SkipEntity(CustomBaseModel):
    entity: Job | Freelancer | list[Freelancer] | Customer
    msg: str | None

    
