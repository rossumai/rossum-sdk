from datetime import datetime

from pydantic import BaseModel, Extra


class Base(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda v: f"{v.isoformat()}Z",
        }
        extra = Extra.ignore
