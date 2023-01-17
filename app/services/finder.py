import logging
import pydantic as pyd

from app.schemas.job import Job, JobStatusEnum
from app.schemas.customer import Customer
from app.schemas.freelancer import Freelancer
from app.schemas.response import MsgResp
from app.notifier import Notifier as notify
from app.settings import app_settings as s

from skip_common_lib.utils.async_http import AsyncHttp
from skip_common_lib.consts import HttpMethod


class FreelancerFinder:
    logger = logging.getLogger("skip-freelancer-finder-service")

    @staticmethod
    async def _get_nearest_available_freelancers(job: Job) -> list:
        response = await AsyncHttp.http_call(
            method=HttpMethod.POST,
            url=f"{s.setting.crud_url}/freelancer/nearest",
            json=dict(
                job_location=job.location,
                job_customer_county=job.customer_county,
                job_category=job.category,
            ),
        )

        return response.json().get("output")

    @staticmethod
    async def _update_and_get_job(
        job_id: str, freelancer_email: str, freelancer_phone: str
    ) -> Job:
        response = await AsyncHttp.http_call(
            method=HttpMethod.PATCH,
            url=f"{s.setting.crud_url}/job/{job_id}",
            params=dict(
                current_job_status=JobStatusEnum.FREELANCER_FINDING, return_with_updated=True
            ),
            json=dict(
                freelancer_email=freelancer_email,
                freelancer_phone=freelancer_phone,
                job_status=JobStatusEnum.FREELANCER_FOUND,
            ),
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

    @classmethod
    async def find(cls, job: Job):
        """Find available and nearest freelancers to the job location
        (which is actually the customer location).

        Args:
            job (Job)

        Returns:
            MsgResp
        """
        available_freelancers = await FreelancerFinder._get_nearest_available_freelancers(job)

        notified_tokens = notify.push_incoming_job(job, available_freelancers)

        return MsgResp(
            msg=f"notification pushed to freelancers {notified_tokens}",
        )

    @classmethod
    @pyd.validate_arguments
    async def take(cls, job_id: str, freelancer: Freelancer) -> MsgResp:
        """Attache a freelancer to a job.

        Args:
            job_id (str): Job ID.
            freelancer (Freelancer): Freelancer that takes the job.

        Returns:
            MsgResp
        """
        job = await FreelancerFinder._update_and_get_job(
            job_id, freelancer.email, freelancer.phone
        )

        customer = await FreelancerFinder._get_customer(job.customer_email)

        # TODO make async
        notify.push_freelancer_found(job, customer)

        return MsgResp(msg=f"notification pushed to customer {customer.email}")
