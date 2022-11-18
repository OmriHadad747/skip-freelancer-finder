import pydantic as pyd
from functools import wraps
from typing import Any, Callable, Dict, Optional
from flask import current_app as app
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
    def save_incoming_job_wrapper(*args):
        _cls = args[0]
        incoming_job_fields: Dict[str, Any] = args[1]

        try:
            incoming_job = job_model.Job(**incoming_job_fields)

            app.logger.debug(f"saving to database the following job {incoming_job.dict()}")

            res = db.add_job(incoming_job)
            if not res.acknowledged:
                return err.db_op_not_acknowledged(incoming_job.dict(), op="insert")

            app.logger.debug(f"job {res.inserted_id} saved to database")

        except pyd.ValidationError as e:
            return err.validation_error(e, incoming_job_fields)
        except Exception as e:
            return err.general_exception(e)

        return find_func(_cls, incoming_job)

    return save_incoming_job_wrapper


def update_incoming_job(take_func: Callable[[Any], Optional[Dict[str, Any]]]):
    """
    Validate given freelancer fields and updates the incoming job in database.

    Args:
        take_func (Callable[[Any], Optional[Dict[str, Any]]]): Decorated function
    """

    @wraps(take_func)
    def update_incoming_job_wrapper(*args):
        _cls = args[0]
        job_id: str = args[1]
        freelancer_fields: Dict[str, Any] = args[2]

        try:
            freelancer = freelancer_model.FreelancerTakeJob(**freelancer_fields)
            job = job_model.JobUpdate(
                **{
                    "freelancer_email": freelancer.freelancer_email,
                    "freelancer_phone": freelancer.freelancer_phone,
                    "job_status": job_model.JobStatusEnum.FREELANCER_FOUND,
                }
            )

            app.logger.debug(f"updating job {job_id} in database with freelancer data")

            res = db.update_job(job_id, job)
            if res.matched_count == 0 and res.modified_count == 0:
                app.logger.debug(f"job {job_id} was already taken by another freelancer")
                return take_func(_cls)

            if not res.acknowledged:
                return err.db_op_not_acknowledged(job.dict(exclude_none=True), op="update")

            app.logger.debug(f"job {job_id} updated in database")

        except pyd.ValidationError as e:
            return err.validation_error(e, freelancer_fields)
        except Exception as e:
            return err.general_exception(e)

        return take_func(_cls, job_id)

    return update_incoming_job_wrapper
