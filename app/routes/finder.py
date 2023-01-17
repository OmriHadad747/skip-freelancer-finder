from fastapi import status

from app.routes import freelancer_finder_router as api
from app.schemas.job import Job
from app.schemas.freelancer import FreelancerTakeJob
from app.schemas.response import MsgResp
from app.services.finder import FreelancerFinder


@api.post("/find", response_model=MsgResp, status_code=status.HTTP_200_OK)
async def find_freelancer(job: Job):
    return await FreelancerFinder.find(job)


@api.post("/take_job/{job_id}", response_model=MsgResp, status_code=status.HTTP_200_OK)
async def take_job(job_id: str, freelancer: FreelancerTakeJob):
    return await FreelancerFinder.take(job_id, freelancer)
