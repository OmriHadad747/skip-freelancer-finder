import logging
import pydantic as pyd

from typing import Any

from app.schemas.job import Job, JobStatusEnum
from app.schemas.customer import Customer
from app.schemas.freelancer import Freelancer, FreelancerTakeJob
from app.schemas.response import MsgResp
from app.schemas.crud_response import SkipEntity
from app.notifier import Notifier as notify
from app.settings import app_settings as s

from skip_common_lib.utils.async_http import AsyncHttp
from skip_common_lib.consts import HttpMethod


class FreelancerFinder:
    logger = logging.getLogger("freelancer-finder-service")

    @classmethod
    @pyd.validate_arguments
    async def _get_nearest_available_freelancers(cls, job: Job) -> list[Freelancer]:
        response = await AsyncHttp.http_call(
            logger=cls.logger,
            method=HttpMethod.POST,
            url=f"{s.setting.crud_url}/freelancer/nearest",
            json=dict(
                job_location=job.location,
                customer_county=job.customer_county,
                job_category=job.category,
            ),
        )

        available_freelancers_list = SkipEntity(**response.json())
        return available_freelancers_list.entity

    @classmethod
    @pyd.validate_arguments
    async def _update_and_get_job(
        cls, job_id: str, to_update: dict[str, Any]
    ) -> Job:
        response = await AsyncHttp.http_call(
            logger=cls.logger,
            method=HttpMethod.PATCH,
            url=f"{s.setting.crud_url}/job/{job_id}",
            params=dict(
                current_job_status=JobStatusEnum.FREELANCER_FINDING.value, return_with_updated=True
            ),
            json=to_update,
        )

        job_entity = SkipEntity(**response.json())
        return job_entity.entity

    @classmethod
    @pyd.validate_arguments
    async def _get_customer(cls, customer_email: str) -> Customer:
        # get the customer who published the job
        response = await AsyncHttp.http_call(
            logger=cls.logger,
            method=HttpMethod.GET,
            url=f"{s.setting.crud_url}/customer/{customer_email}",
        )

        customer_entity = SkipEntity(**response.json())
        return customer_entity.entity

    @classmethod
    @pyd.validate_arguments
    async def find(cls, job: Job):
        """Find available and nearest freelancers to the job location
        (which is actually the customer location).

        Args:
            job (Job)

        Returns:
            MsgResp
        """
        cls.logger.info(f"finding freelancer for job {job.id}.")

        available_freelancers = await FreelancerFinder._get_nearest_available_freelancers(job)

        notified_tokens = notify.push_incoming_job(job, available_freelancers)

        return MsgResp(
            msg=f"notification pushed to freelancers {notified_tokens}",
        )

    @classmethod
    @pyd.validate_arguments
    async def take(cls, job_id: str, freelancer: FreelancerTakeJob) -> MsgResp:
        """Attache a freelancer to a job.

        Args:
            job_id (str): Job ID.
            freelancer (FreelancerTakeJob): Freelancer that takes the job.

        Returns:
            MsgResp
        """
        cls.logger.info(f"freelancer {freelancer.email} takes job {job_id}")

        job = await FreelancerFinder._update_and_get_job(
            job_id,
            to_update=dict(
                freelancer_email=freelancer.email,
                freelancer_phone=freelancer.phone,
                status=JobStatusEnum.FREELANCER_FOUND.value,
            ),
        )

        customer = await FreelancerFinder._get_customer(job.customer_email)

        # TODO make async
        notify.push_freelancer_found(job, customer)

        return MsgResp(msg=f"notification pushed to customer {customer.email}")
