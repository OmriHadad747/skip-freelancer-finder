import flask

from typing import Tuple
from flask import Blueprint
from flask import request
from app.services.finder import FreelancerFinder


freelancer_finder_bp = Blueprint("freelancer_finder_bp", "freelancer_finder")


@freelancer_finder_bp.post("/find")
def find_freelancer() -> Tuple[flask.Response, int]:
    return FreelancerFinder.find(request.json)


@freelancer_finder_bp.post("/take_job/<string:id>")
def take_job(id: str):
    return FreelancerFinder.take(id, request.json)

