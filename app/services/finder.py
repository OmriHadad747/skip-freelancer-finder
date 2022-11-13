import flask
from typing import Any, Dict, List, Tuple
from pydantic import validate_arguments
from pymongo import command_cursor
from flask import jsonify
from firebase_admin import messaging
from app.models import job as job_model
from app.models import freelancer as freelancer_model
from app import middlewares
from app.services.db import FreelancerDatabase as freelancers_db
from app.services.db import JobDatabase as job_db


class FreelancerFinder:

    
    @staticmethod
    def _exclude_failed_tokens(tokens: List[str], resps: List[messaging.SendResponse]):
        # TODO write docstring
        # TODO log here
        failed_tokens = [tokens[idx] for idx, resp in enumerate(resps) if not resp.sucess]

        # TODO implement the call to the db function that remove the registration token from freelancers


    @classmethod
    # TODO type this method
    # TODO type argument
    def _nofity_freelancers(cls, job: job_model.Job, freelancers: command_cursor.CommandCursor):
        # TODO write docstring
        # TODO log here
        tokens = [f.get("registration_token") for f in freelancers]
        # TODO log here the tokens we fetched

        msg = messaging.MulticastMessage(
            data={
                "job_id": job.id,
                "job_description": job.job_description,
                "customer_email": job.customer_email,
                "customer_phone": job.customer_phone,
                "customer_address": job.customer_address,
                "customer_county": job.customer_county
            },
            tokens=tokens
        )
        resp: messaging.BatchResponse = messaging.send_multicast(msg, dry_run=True)
        if resp.failure_count > 0:
            cls._exclude_failed_tokens(tokens, resp.responses)

        # TODO log here how many notified


    @classmethod
    @validate_arguments
    @middlewares.save_incoming_job
    def find(cls, incoming_job: job_model.Job) -> Tuple[flask.Response, int]:
        # TODO write docstring
        try:
            available_freelancers = freelancers_db.find(incoming_job)
            cls._nofity_freelancers(incoming_job, available_freelancers)

        except Exception as e:
            # TODO handle exception here
            pass

        return jsonify(message="notification pushed to freelancers successfully"), 200


    @classmethod
    @validate_arguments
    @middlewares.update_incoming_job
    def take(cls, job_id: str, freelancer: freelancer_model.Freelancer):
        # TODO write docstring
        try:
            job = job_db.get_job_by_id(job_id)
            job.freelancer_email = freelancer.email
            job.freelancer_phone = freelancer.phone

        except Exception as e:
            # TODO handle exception here
            pass