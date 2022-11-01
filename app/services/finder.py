import requests

from typing import Any, Dict, Optional
from pydantic import validate_arguments
from flask import jsonify
from flask import current_app as app
from app.services.db import FreelancerDatabase as db


class FreelancerFinder:

    @staticmethod
    def _get_customer(email: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"http://{app.config['CRUD_HOST']}/customer/{email}"
            resp = requests.get(url, headers={"Content-Type": "application/json"})
            if resp.status_code != 200:
                # TODO log here
                return None

            return resp.json().get("customer")

        except Exception as e:
            # TODO handle exception here
            pass

    
    @staticmethod
    def _nofity_freelancers(freelancers):
        for f in freelancers:
            print(f)
        print()


    @classmethod
    @validate_arguments
    def find(cls, job: Dict[str, Any]):
        try:
            customer_email = job.get("customer_email")
            customer = cls._get_customer(customer_email)
            customer_county = customer.get("county")
            customer_lon = -73.9667
            customer_lat = 40.78

            available_freelancers = db.find(customer_county, customer_lon, customer_lat)
            cls._nofity_freelancers(available_freelancers)

        except Exception as e:
            # TODO handle exception here
            pass

        return jsonify(message="finding..."), 200