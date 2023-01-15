import logging
import pydantic as pyd

from app.schemas.job import Job, JobUpdate, JobQuotation
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
            json=JobUpdate(job_quotation=quotation).dict(),
        )

        # get corresponding job
        response = await AsyncHttp.http_call(
            method=HttpMethod.GET, url=f"{s.setting.crud_url}/job/{job_id}"
        )
        job = Job(**response.json())

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
        # get corresponding job
        job = Job(**jobs_db.get_job_by_id(job_id))

        # get corresponding freelancer
        freelancer = Freelancer(**freelancers_db.get_freelancer_by_email(job.freelancer_email))

        notify.push_quotation_confirmation(job, freelancer)

        return MsgResp(msg=f"notification pushed to freelancer {freelancer.email}")
