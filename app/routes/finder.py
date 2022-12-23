from fastapi import status

from app.routes import freelancer_finder_router as api
from app.services.finder import FreelancerFinder
from skip_common_lib.schemas import job as job_schema
from skip_common_lib.schemas import freelancer as freelancer_schema
from skip_common_lib.schemas import response as resp_schema


@api.post("/find", response_model=resp_schema.MsgResponse, status_code=status.HTTP_200_OK)
async def find_freelancer(job: job_schema.Job):
    return await FreelancerFinder.find(job)


@api.post(
    "/take_job/{job_id}", response_model=resp_schema.MsgResponse, status_code=status.HTTP_200_OK
)
async def take_job(job_id: str, freelancer: freelancer_schema.FreelancerTakeJob):
    return await FreelancerFinder.take(job_id, freelancer)
