from functools import wraps
from typing import Any, Dict
from app.models import job as job_model
from app.utils.errors import Errors as err
from app.services.db import JobDatabase as db


# TODO type the 'find_func' argument
def save_incoming_job(find_func):
    # TODO write docstring
    @wraps(find_func)
    def save_incoming_job_wrapper(fields: Dict[str, Any]):
        try:
            incoming_job = job_model.Job(**fields)
            incoming_job.customer_lon = -73.9667
            incoming_job.customer_lat = 40.78

            ack = db.add_job(incoming_job)
            if not ack:
                return err.db_op_not_acknowledged(incoming_job.dict(), op="insert")

        except Exception as e:
            return err.general_exception(e)

        return find_func(incoming_job)        

    return save_incoming_job_wrapper


def update_incoming_job(take_func):
    
    def update_incoming_job_wrapper():
        pass

    return update_incoming_job_wrapper





# # TODO type the 'find_func' argument
# def fetch_customer(find_func):
#     # TODO write docstring
#     @wraps(find_func)
#     def fetch_customer_wrapper(incoming_job: job_model.Job):
#         # TODO log here - f"fetching a customer related to the incoming job {incoming_job.id}""
#         try:
#             url = f"http://{app.config['CRUD_HOST']}/customer/{incoming_job.customer_email}"
#             resp = requests.get(url, headers={"Content-Type": "application/json"})
#             if resp.status_code != 200:
#                 # TODO log here - f"the following response code {resp.status_code} returns from {url}"
#                 return None
        
#             customer = customer_model.Customer(**resp.json().get("customer"))
#             # TODO use 3rd party api to fetch customer lon & lat if 
#             # the customer does not have already. this should happen single time for
#             # each customer
#             customer.lon 
#             customer.lat = 40.78
        
#         except Exception as e:
#             return err.general_exception(e)

#         return find_func(incoming_job, customer)

#     return fetch_customer_wrapper