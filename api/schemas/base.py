from pydantic import BaseModel, ConfigDict

class BaseInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
