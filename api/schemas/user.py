from pydantic import BaseModel
from domain import UserRole
from .base import BaseInput



class UserLogin(BaseInput):
    username: str
    password: str


class UserRegister(BaseInput):
    username: str
    password: str
    role: UserRole