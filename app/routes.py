from typing import Dict, Tuple
from flask import Blueprint
from flask import request
from app.services.finder import FreelancerFinder


freelancer_finder_bp = Blueprint("freelancer_finder_bp", "freelancer_finder")


@freelancer_finder_bp.post("/find")
def find_freelancer() -> Tuple[Dict, int]:
    return FreelancerFinder.find(request.json)