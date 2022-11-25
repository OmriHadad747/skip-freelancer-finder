import flask
import pydantic as pyd

from typing import List, Tuple
from pymongo import command_cursor
from flask import jsonify
from flask import current_app as app
from firebase_admin import messaging

from skip_common_lib.middleware import freelancer_finder as middlwares
from skip_common_lib.models import job as job_model
from skip_common_lib.models import customer as customer_model
from skip_common_lib.database.jobs import JobDatabase as jobs_db
from skip_common_lib.database.customers import CustomerDatabase as customers_db
from skip_common_lib.database.freelancers import FreelancerDatabase as freelancers_db
from skip_common_lib.utils.errors import Errors as err
from skip_common_lib.utils.notifier import Notifier as notify


class FreelancerFinder:
    @classmethod
    @middlwares.save_incoming_job
    def find(cls, incoming_job: job_model.Job) -> Tuple[flask.Response, int]:
        """Find available and nearest freelancers to the job location
        (which is actually the customer location) using skip-db-lib.

        Args:
            incoming_job (job_model.Job)

        Returns:
            Tuple[flask.Response, int]
        """
        try:
            app.logger.debug(
                f"searching neareast freelancers to customer location | lon: {incoming_job.job_location[0]} | lat: {incoming_job.job_location[1]}"
            )

            available_freelancers = freelancers_db.find_nearest_freelancers(incoming_job)
            notified_tokens = notify.push_incoming_job(incoming_job, available_freelancers)

        except Exception as e:
            return err.general_exception(e)

        return (
            jsonify(message=f"notification pushed to freelancers {notified_tokens}"),
            200,
        )

    @classmethod
    @middlwares.update_incoming_job
    def take(cls, job_id: str = None) -> Tuple[flask.Response, int]:
        """In case the given 'job_id' equals None, you can assume that the job already
        taken by another freelancer.

        Otherwise, fetch the job and corresponded customer from the database
        using the given 'job_id'.
        Eventually, notifies the customer that a freelancer was found.

        Args:
            job_id (str, optional): An id of a job. Defaults to None.

        Returns:
            Tuple[flask.Response, int]
        """
        if not job_id:
            return jsonify(message="job was already taken by another freelancer"), 400

        try:
            # get the job
            job = job_model.Job(**jobs_db.get_job_by_id(job_id))

            # get the customer posted the job
            customer = customer_model.Customer(
                **customers_db.get_customer_by_email(job.customer_email)
            )

            notify.push_freelancer_found(job, customer)

        except pyd.ValidationError as e:
            return err.validation_error(e)
        except Exception as e:
            return err.general_exception(e)

        return jsonify(message=f"notification pushed to customer {customer.email}"), 200
