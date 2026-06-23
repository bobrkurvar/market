from .base import BaseInput
from pydantic import Field, BaseModel

class ReviewCreate(BaseInput):
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Оценка покупателя (от 1 до 5)"
    )
    comment: str = Field(
        ...,
        max_length=2000,
        description="Текст отзыва (опционально)"
    )

class ReviewRead(BaseModel):
    rating: int
    comment: str
    class Config:
        from_attributes = True