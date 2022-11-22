import flask
import pydantic as pyd

from typing import List, Tuple
from pymongo import command_cursor
from flask import jsonify
from flask import current_app as app
from firebase_admin import messaging

from skip_common_lib.middleware import freelancer_finder as middlwares
from skip_common_lib.utils.errors import Errors as err
from skip_common_lib.models import job as job_model
from skip_common_lib.models import customer as customer_model
from skip_common_lib.database.jobs import JobDatabase as jobs_db
from skip_common_lib.database.customers import CustomerDatabase as customers_db
from skip_common_lib.database.freelancers import FreelancerDatabase as freelancers_db


class FreelancerFinder:
    @staticmethod
    def _exclude_failed_tokens(tokens: List[str], resps: List[messaging.SendResponse]) -> List[str]:
        """Finds the failed registration tokens in 'resps' and remove
        them from database cause they are proably invalid.

        Args:
            tokens (List[str]): Registration tokens that a notification pushed to.
            resps (List[messaging.SendResponse]): List of responses from each notification for each freelancer notified.

        Returns:
            List[str]: List of all the registration tokens that actually notified
        """
        failed_tokens = [tokens[idx] for idx, resp in enumerate(resps) if not resp.success]
        app.logger.debug(f"discarding invalid registration tokens {failed_tokens}")

        # TODO implement the call to the db function that remove the registration token from freelancers
        # implement here during testing with real registration tokens

        return [t for t in failed_tokens if t not in tokens]

    @classmethod
    def _nofity_freelancers(
        cls, job: job_model.Job, freelancers: command_cursor.CommandCursor
    ) -> List[str]:
        """Found the registration token for each freelancer, and eventually
        trying to push notification for all of them.

        If there are failures with some registation tokens, deleting them frm
        database.

        Args:
            job (job_model.Job): A job to notify freelancers about.
            freelancers (command_cursor.CommandCursor): Cursor of available freelancers

        Returns:
            List[str]: List of all the registration tokens that actually notified
        """
        app.logger.info("notifying freelancers about incoming job")

        tokens = [f.get("registration_token") for f in freelancers]

        msg = messaging.MulticastMessage(data=job.job_to_str(), tokens=tokens)
        resp: messaging.BatchResponse = messaging.send_multicast(msg, dry_run=True)
        # TODO unfreeze here when working with real registration tokens
        # if resp.failure_count > 0:
        #     return cls._exclude_failed_tokens(tokens, resp.responses)

        app.logger.debug(
            f"from {tokens} | {resp.success_count} notified | {resp.failure_count} not notified"
        )
        return tokens

    @classmethod
    @pyd.validate_arguments
    def _notify_customer(cls, job: job_model.Job, customer: customer_model.Customer) -> None:
        """Notify a customer that a freelancer has been found for his job

        Args:
            job (job_model.Job): Customer's job.
            customer (customer_model.Customer): Customer to notify.
        """
        app.logger.info("notifying customer that a freelancer was found")

        msg = messaging.Message(
            data=job.job_to_str(freelancer_part=True), token=customer.registration_token
        )
        # resp = messaging.send(msg, dry_run=True)
        resp = None
        app.logger.debug(f"customer notified with message {resp}")

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
            notified_tokens = cls._nofity_freelancers(incoming_job, available_freelancers)

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

            cls._notify_customer(job, customer)

        except pyd.ValidationError as e:
            return err.validation_error(e)
        except Exception as e:
            return err.general_exception(e)

        return jsonify(message=f"notification pushed to customer {customer.email}"), 200
