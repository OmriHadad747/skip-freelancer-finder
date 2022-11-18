import flask

from typing import List, Tuple
from pymongo import command_cursor
from flask import jsonify
from flask import current_app as app
from firebase_admin import messaging
from app import middlewares
from app.utils.errors import Errors as err
from skip_db_lib.models import job as job_model
from skip_db_lib.models import customer as customer_model
from skip_db_lib.database.freelancers import FreelancerDatabase as freelancers_db
from skip_db_lib.database.jobs import JobDatabase as jobs_db
from skip_db_lib.database.customers import CustomerDatabase as customers_db


class FreelancerFinder:
    @staticmethod
    def _exclude_failed_tokens(tokens: List[str], resps: List[messaging.SendResponse]) -> None:
        # TODO write docstring
        failed_tokens = [tokens[idx] for idx, resp in enumerate(resps) if not resp.success]

        app.logger.debug(f"discarding invalid registration tokens {failed_tokens}")

        # TODO implement the call to the db function that remove the registration token from freelancers

    @classmethod
    def _nofity_freelancers(
        cls, job: job_model.Job, freelancers: command_cursor.CommandCursor
    ) -> None:
        # TODO write docstring
        app.logger.info("notifying freelancers about incoming job")

        tokens = [f.get("registration_token") for f in freelancers]

        msg = messaging.MulticastMessage(data=job.job_to_str(), tokens=tokens)
        resp: messaging.BatchResponse = messaging.send_multicast(msg, dry_run=True)
        if resp.failure_count > 0:
            cls._exclude_failed_tokens(tokens, resp.responses)

        app.logger.debug(f"{resp.success_count} notified | {resp.failure_count} not notified")

    @classmethod
    def _notify_customer(cls, job: job_model.Job, customer: customer_model.Customer) -> None:
        # TODO write docstring
        app.logger.info("notifying customer that a freelancer was found")

        msg = messaging.Message(data=job.job_to_str(freelancer_part=True), token=customer.registration_token)
        # resp = messaging.send(msg, dry_run=True)
        # TODO validate that message was sent somehow

        app.logger.info("customer notified")

    @classmethod
    @middlewares.save_incoming_job
    def find(cls, incoming_job: job_model.Job) -> Tuple[flask.Response, int]:
        """
        Find available and nearest freelancers to the job location
        (which is actually the customer location) using skip-db-lib.

        Args:
            incoming_job (job_model.Job): _description_

        Returns:
            Tuple[flask.Response, int]
        """
        try:
            app.logger.debug(
                f"searching neareast freelancers to customer location | lon: {incoming_job.customer_lon} | lat: {incoming_job.customer_lat}"
            )

            available_freelancers = freelancers_db.find_nearest_freelancers(incoming_job)
            cls._nofity_freelancers(incoming_job, available_freelancers)

        except Exception as e:
            return err.general_exception(e)

        return jsonify(message="notification pushed to freelancers"), 200

    @classmethod
    @middlewares.update_incoming_job
    def take(cls, job_id: str = None) -> Tuple[flask.Response, int]:
        """
        In case the given 'job_id' equals None, you can assume that the job already
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

            cls._notify_customer(job, customer)

        except Exception as e:
            return err.general_exception(e)

        return jsonify(message=f"freelancer found for {job_id}"), 200
