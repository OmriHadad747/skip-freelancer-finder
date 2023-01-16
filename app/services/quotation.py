import logging
import pydantic as pyd

from app.schemas.job import Job, JobQuotation, JobUpdate, JobStatusEnum
from app.schemas.customer import Customer
from app.schemas.freelancer import Freelancer
from app.schemas.response import MsgResp
from app.settings import app_settings as s

from skip_common_lib.middleware import job_quotation as middleware
from skip_common_lib.utils.notifier import Notifier as notify
from skip_common_lib.utils.async_http import AsyncHttp
from skip_common_lib.consts import HttpMethod


class JobQuotation:
    logger = logging.getLogger("skip-freelancer-finder-service")

    @classmethod
    @pyd.validate_arguments
    @middleware.update_job_quotation
    async def quote(cls, job_id: str, quotation: JobQuotation):
        # update quotation in job
        response = await AsyncHttp.http_call(
            method=HttpMethod.PATCH,
            url=f"{s.setting.crud_url}/job/{job_id}",
            params=dict(current_job_status=JobStatusEnum.FREELANCER_FOUND, return_with_updated=True),
            json=JobUpdate(job_quotation=quotation).dict(),
        )

        job = Job(**response.json().get("entity"))

        # get corresponding customer
        response = await AsyncHttp.http_call(
            method=HttpMethod.GET, url=f"{s.setting.crud_url}/customer/{job.customer_email}"
        )
        customer = Customer(**response.json())

        notify.push_job_quotation(quotation, customer)

        return MsgResp(msg=f"notification pushed to customer {customer.email}")

    @classmethod
    @pyd.validate_arguments
    @middleware.update_job_approved_or_declined
    async def confirm(cls, job_id: str, confirmation: bool):
        # update quotation in job
        response = await AsyncHttp.http_call(
            method=HttpMethod.PATCH,
            url=f"{s.setting.crud_url}/job/{job_id}",
            params=dict(job_status=JobStatusEnum.FREELANCER_FOUND, return_with_updated=True),
            json=JobUpdate(
                job_status=JobStatusEnum.APPROVED if confirmation else JobStatusEnum.CUSTOMER_CANCELD
            )
        )
        # get corresponding job
        job = Job(**response.json().get("entity"))

        # get corresponding freelancer
        response = await AsyncHttp.http_call(
            method=HttpMethod.GET, url=f"{s.setting.crud_url}/freelancer/{job.freelancer_email}"
        )
        freelancer = Freelancer(**response.json())

        notify.push_quotation_confirmation(job, freelancer)

        return MsgResp(msg=f"notification pushed to freelancer {freelancer.email}")
