from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Operations(StrEnum):
    exact = "exact"
    gte = "gte"
    lte = "lte"
    gt = "gt"
    lt = "lt"
    ilike = "ilike"
    in_ = "in"
    ne = "ne"
    is_ = "is"
    is_not = "is_not"


@dataclass
class DomainFilter:
    model: type  # Доменная модель (например, Category)
    field: str  # Имя поля (например, 'name')
    value: Any  # Значение (например, 'Керамика')


@dataclass
class Operation:
    value: Any
    # op: str = "exact"  # По умолчанию обычное равенство
    op: Operations
