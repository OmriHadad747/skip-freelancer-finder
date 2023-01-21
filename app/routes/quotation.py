from fastapi import status

from app.routes import job_quotation_router as api
from app.schemas.job import JobQuotation
from app.schemas.response import MsgResp
from app.services.quotation import JobQuot


@api.post("/quotation/{job_id}", status_code=status.HTTP_200_OK, response_model=MsgResp)
async def post_quotation(job_id: str, job: JobQuotation):
    return await JobQuot.quote(job_id, job)


@api.post(
    "/quotation/{job_id}/confirmation", status_code=status.HTTP_200_OK, response_model=MsgResp
)
async def confirm_quotation(job_id: str, confirmation: bool):
    return await JobQuot.confirm(job_id, confirmation)
