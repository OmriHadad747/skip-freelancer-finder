import pydantic as pyd

from fastapi.responses import JSONResponse
from fastapi import status


class CustomBaseModel(pyd.BaseModel):
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class CustomRespBaseModel(pyd.BaseModel):
    class Config:
        pass

    def json_response(self, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        return JSONResponse(content=self.dict(), status_code=status_code)
