from typing import Any, Dict, Tuple
from flask import jsonify


class Errors:
    @classmethod
    def validation_error(
        cls, exc: Exception, to_validate: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], int]:
        return jsonify(to_validate=to_validate, error_msg=str(exc)), 400

    @classmethod
    def general_exception(cls, exc: Exception) -> Tuple[Dict[str, Any], int]:
        return jsonify(err_msg=str(exc)), 400

    @classmethod
    def db_op_not_acknowledged(cls, obj: Dict[str, Any], op: str) -> Tuple[Dict[str, Any], int]:
        return jsonify(err_msg=f"db operation {op.upper()} on {obj} doesn't acknowledged"), 400

    @classmethod
    def login_failed(cls):
        return jsonify(err_msg="failed to login, probably because invalid email or password")
