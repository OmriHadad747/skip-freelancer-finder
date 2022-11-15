import pydantic as pyd
from functools import wraps
from typing import Any, Callable, Dict, Optional
from app.utils.errors import Errors as err
from skip_db_lib.models import job as job_model
from skip_db_lib.models import freelancer as freelancer_model
from skip_db_lib.database.jobs import JobDatabase as db


def save_incoming_job(find_func: Callable[[Any], Optional[Dict[str, Any]]]):
    """
    Validates and save the incoming job to database.
    Eventually, pushing forwared to the decorated function a validate job model.

    Args:
        find_func (Callable[[Any], Optional[Dict[str, Any]]]): Decorated function
    """

    @wraps(find_func)
    def save_incoming_job_wrapper(incoming_job_fields: Dict[str, Any]):
        # TODO log here DEBUG - f"saving to database the following job {incoming_job_fields}"
        try:
            incoming_job = job_model.Job(**incoming_job_fields)
            # TODO delete the following 2 lines once the location is enabled
            # by the customer application
            incoming_job.customer_lon = -73.9667
            incoming_job.customer_lat = 40.78

            res = db.add_job(incoming_job)
            if not res.acknowledged:
                return err.db_op_not_acknowledged(incoming_job.dict(), op="insert")

            # TODO log here DEBUG - f"job {res.inserted_id} saved to database successfully"

        except pyd.ValidationError as e:
            return err.validation_error(e, incoming_job_fields)
        except Exception as e:
            return err.general_exception(e)

        return find_func(incoming_job)

    return save_incoming_job_wrapper


def update_incoming_job(take_func: Callable[[Any], Optional[Dict[str, Any]]]):
    """
    Validate given freelancer fields and updates the incoming job in database.

    Args:
        take_func (Callable[[Any], Optional[Dict[str, Any]]]): Decorated function
    """

    @wraps(take_func)
    def update_incoming_job_wrapper(job_id: str, freelancer_fields: Dict[str, Any]):
        # TODO log here DEBUG - f"updating job {job_id} in database with freelancer data"
        try:
            freelancer = freelancer_model.Freelancer(**freelancer_fields)
            job = job_model.JobUpdate(
                **{
                    "freelancer_email": freelancer.email,
                    "freelancer_phone": freelancer.phone,
                    "job_status": job_model.JobStatusEnum.FREELANCER_FOUND,
                }
            )

            res = db.update_job(job_id, job)
            if res.matched_count == 0 and res.modified_count == 0:
                # TODO log here DEBUG - f"job {job_id} was already taken by another freelancer"
                return take_func()

            if not res.acknowledged:
                return err.db_op_not_acknowledged(job.dict(exclude_none=True), op="update")

            # TODO log here DEBUG - f"job {job_id} updated in database successfully"

        except pyd.ValidationError as e:
            return err.validation_error(e, freelancer_fields)
        except Exception as e:
            return err.general_exception(e)

        return take_func(job_id)

    return update_incoming_job_wrapper
