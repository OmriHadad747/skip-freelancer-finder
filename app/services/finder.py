import logging
import pydantic as pyd

from app.schemas.job import Job, JobUpdate, JobStatusEnum
from app.schemas.customer import Customer
from app.schemas.freelancer import Freelancer
from app.schemas.response import MsgResp
from app.settings import app_settings as s

from skip_common_lib.middleware import job_quotation as middleware
from skip_common_lib.utils.notifier import Notifier as notify
from skip_common_lib.utils.async_http import AsyncHttp
from skip_common_lib.consts import HttpMethod


class FreelancerFinder:
    logger = logging.getLogger("skip-freelancer-finder-service")

    @classmethod
    async def find(cls, incoming_job: Job):
        """Find available and nearest freelancers to the job location
        (which is actually the customer location) using skip-db-lib.

        Args:
            incoming_job (Job)

        Returns:
            MsgResp
        """
        try:
            cls.logger.debug(
                f"searching neareast freelancers to customer location | lon: {incoming_job.job_location[0]} | lat: {incoming_job.job_location[1]}"
            )

            # available_freelancers = await freelancers_db.find_nearest_freelancers(incoming_job)
            # TODO make the next call async
            # notified_tokens = notify.push_incoming_job(incoming_job, available_freelancers)

        except Exception as e:
            return err.general_exception(e)

        return MsgResp(
            msg=f"notification pushed to freelancers {notified_tokens}",
        )

    @classmethod
    @pyd.validate_arguments
    async def take(cls, job_id: str, freelancer: Freelancer):
        """In case the given 'job_id' equals None, you can assume that the job already
        taken by another freelancer.

        Otherwise, fetch the job and corresponded customer from the database
        using the given 'job_id'.
        Eventually, notifies the customer that a freelancer was found.

        Args:
            job_id (str, optional): An id of a job. Defaults to None.

        Returns:
            resp_schema.MsgResponse
        """
        # update quotation in job
        response = await AsyncHttp.http_call(
            method=HttpMethod.PATCH,
            url=f"{s.setting.crud_url}/job/{job_id}",
            params=dict(current_job_status=JobStatusEnum.FREELANCER_FINDING, return_with_updated=True),
            json=JobUpdate(
                freelancer_email=freelancer.email,
                freelancer_phone=freelancer.phone,
                job_status=JobStatusEnum.FREELANCER_FOUND

            ).dict(),
        )

        job = Job(**response.json().get("entity"))

        # get the customer who published the job
        response = await AsyncHttp.http_call(
            method=HttpMethod.GET,
            url=f"{s.setting.crud_url}/customer/{job.customer_email}",
        )

        customer = Customer(**response.json().get("output"))

        # TODO make async
        notify.push_freelancer_found(job, customer)

        return MsgResp(
            msg=f"notification pushed to customer {customer.email}"
        )
