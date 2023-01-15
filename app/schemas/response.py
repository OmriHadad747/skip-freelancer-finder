from typing import Any

from app.schemas import CustomRespBaseModel


class MsgResp(CustomRespBaseModel):
    msg: str


class EntityResp(CustomRespBaseModel):
    output: dict[str, Any]
