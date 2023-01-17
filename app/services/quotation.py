import logging
from typing import Any
import pydantic as pyd

from app.schemas.job import Job, JobQuotation, JobUpdate, JobStatusEnum
from app.schemas.customer import Customer
from app.schemas.freelancer import Freelancer
from app.schemas.response import MsgResp
from app.notifier import Notifier as notify
from app.settings import app_settings as s

from skip_common_lib.utils.async_http import AsyncHttp
from skip_common_lib.consts import HttpMethod


class JobQuot:
    logger = logging.getLogger("skip-freelancer-finder-service")

    @staticmethod
    async def _update_and_get_job(job_id: str, to_update: dict[str, Any]) -> Job:
        response = await AsyncHttp.http_call(
            # update quotation in job
            method=HttpMethod.PATCH,
            url=f"{s.setting.crud_url}/job/{job_id}",
            params=dict(
                current_job_status=JobStatusEnum.FREELANCER_FOUND, return_with_updated=True
            ),
            json=to_update,
        )

        return Job(**response.json().get("entity"))

    @staticmethod
    async def _get_customer(customer_email: str) -> Customer:
        # get the customer who published the job
        response = await AsyncHttp.http_call(
            method=HttpMethod.GET,
            url=f"{s.setting.crud_url}/customer/{customer_email}",
        )

        return Customer(**response.json().get("output"))

    @staticmethod
    async def _get_freelancer(freelancer_email: str) -> Freelancer:
        # get the freelancer who quoted the job
        response = await AsyncHttp.http_call(
            method=HttpMethod.GET,
            url=f"{s.setting.crud_url}/freelacner/{freelancer_email}",
        )

        return Freelancer(**response.json().get("output"))

    @classmethod
    @pyd.validate_arguments
    async def quote(cls, job_id: str, quotation: JobQuotation):
        job = await JobQuot._update_and_get_job(job_id, to_update=dict(job_quotation=quotation))

        customer = await JobQuot._get_customer(job.customer_email)

        notify.push_job_quotation(quotation, customer)

        return MsgResp(msg=f"notification pushed to customer {customer.email}")

    @classmethod
    @pyd.validate_arguments
    async def confirm(cls, job_id: str, confirmation: bool):
        job = await JobQuot._update_and_get_job(
            job_id,
            to_update=dict(
                job_status=JobStatusEnum.APPROVED
                if confirmation
                else JobStatusEnum.CUSTOMER_CANCELD
            ),
        )

        freelancer = await JobQuot._get_freelancer(job.freelancer_email)

        notify.push_quotation_confirmation(job, freelancer)

        return MsgResp(msg=f"notification pushed to freelancer {freelancer.email}")
