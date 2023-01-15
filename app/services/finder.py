import logging
import pydantic as pyd

from skip_common_lib.middleware import freelancer_finder as middlwares
from app.schemas.job import Job
from app.schemas.response import MsgResp
from skip_common_lib.utils.errors import Errors as err
from skip_common_lib.utils.notifier import Notifier as notify


class FreelancerFinder:
    logger = logging.getLogger("skip-freelancer-finder-service")

    @classmethod
    @middlwares.save_incoming_job
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

            available_freelancers = await freelancers_db.find_nearest_freelancers(incoming_job)
            # TODO make the next call async
            notified_tokens = notify.push_incoming_job(incoming_job, available_freelancers)

        except Exception as e:
            return err.general_exception(e)

        return MsgResp(
            msg=f"notification pushed to freelancers {notified_tokens}",
        )

    @classmethod
    @middlwares.update_incoming_job
    async def take(cls, job_id: str = None):
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
        if not job_id:
            return resp_schema.MsgResponse(
                args=dict(job_id=job_id), msg="job was already taken by another freelancer"
            )

        try:
            # get the job
            job = await jobs_db.get_job_by_id(job_id)
            job = Job(**job)

            # get the customer posted the job
            customer = await customers_db.get_customer_by_email(job.customer_email)
            customer = customer_model.Customer(**customer)

            # TODO make the next call async
            notify.push_freelancer_found(job, customer)

        except pyd.ValidationError as e:
            return err.validation_error(e)
        except Exception as e:
            return err.general_exception(e)

        return resp_schema.MsgResponse(
            args=dict(job_id=job_id), msg=f"notification pushed to customer {customer.email}"
        )
