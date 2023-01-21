import pydantic as pyd

from firebase_admin import messaging

from app.schemas.job import Job, JobQuotation
from app.schemas.freelancer import Freelancer
from app.schemas.customer import Customer


class Notifier:
    @staticmethod
    def _exclude_failed_tokens(tokens: list[str], resps: list[messaging.SendResponse]) -> list[str]:
        """Finds the failed registration tokens in 'resps' and remove
        them from database cause they are proably invalid.

        Args:
            tokens (list[str]): Registration tokens that a notification pushed to.
            resps (list[messaging.SendResponse]): List of responses from each notification for each freelancer notified.

        Returns:
            list[str]: list of all the registration tokens that actually notified
        """
        failed_tokens = [tokens[idx] for idx, resp in enumerate(resps) if not resp.success]
        # app.logger.debug(f"discarding invalid registration tokens {failed_tokens}")

        # TODO implement the call to the db function that remove the registration token from freelancers
        # implement here during testing with real registration tokens

        return [t for t in failed_tokens if t not in tokens]

    @classmethod
    @pyd.validate_arguments
    def push_incoming_job(cls, job: Job, freelancers: list[Freelancer]) -> list[str]:
        """Found the registration token for each freelancer, and eventually
        trying to push notification for all of them.

        If there are failures with some registation tokens, deleting them frm
        database.

        Args:
            job (Job): A job to notify freelancers about.
            freelancers (list[Freelancer]): List of available freelancers.

        Returns:
            list[str]: list of all the registration tokens that actually notified.
        """
        # app.logger.info("notifying freelancers about incoming job")

        tokens = [f.registration_token for f in freelancers]

        msg = messaging.MulticastMessage(data=job.job_to_str(), tokens=tokens)
        resp: messaging.BatchResponse = messaging.send_multicast(msg, dry_run=True)
        # TODO unfreeze here when working with real registration tokens
        # if resp.failure_count > 0:
        #     return cls._exclude_failed_tokens(tokens, resp.responses)

        # app.logger.debug(
        #     f"from {tokens} | {resp.success_count} notified | {resp.failure_count} not notified"
        # )
        return tokens

    @classmethod
    @pyd.validate_arguments
    def push_freelancer_found(cls, job: Job, customer: Customer) -> None:
        """Notify a customer that a freelancer has been found for his job

        Args:
            job (Job): Customer's job.
            customer (Customer): Customer to notify.
        """
        # app.logger.info("notifying customer that a freelancer was found")

        msg = messaging.Message(
            data=job.job_to_str(freelancer_part=True), token=customer.registration_token
        )
        # resp = messaging.send(msg, dry_run=True)

        # app.logger.debug(f"customer notified with message {resp}")

    @classmethod
    @pyd.validate_arguments
    def push_job_quotation(cls, quotation: JobQuotation, customer: Customer) -> None:
        # TODO write docstring
        # app.logger.info("notifying customer about job quotation")

        msg = messaging.Message(
            data=quotation.quotation_to_str(), token=customer.registration_token
        )
        # resp = messaging.send(msg, dry_run=True)

        # app.logger.debug(f"customer notified with message {resp}")

    @classmethod
    @pyd.validate_arguments
    def push_quotation_confirmation(
        cls,
        job: Job,
        freelancer: Freelancer,
    ) -> None:
        # TODO write docstring
        # app.logger.info(
        #     f"notifying freelancer {freelancer.email} about job quotation approved/canceld for job {job.id}"
        # )

        msg = messaging.Message(
            data=job.job_to_str(freelancer_part=True),
            tokens=freelancer.registration_token,
        )
        # resp = messaging.send(msg, dry_run=True)

        # app.logger.debug(f"freelancer notified with message {resp}")
