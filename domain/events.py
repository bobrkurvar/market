from dataclasses import dataclass


class Event:
    """Базовый класс для всех событий"""

    pass


@dataclass
class OrderCreatedEvent(Event):
    order_id: int
    total_cost: float
    product_title: str
