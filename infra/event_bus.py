import logging
from typing import Callable, Dict, List, Type

from domain import Event

log = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._subscribers: Dict[Type[Event], List[Callable]] = {}

    def subscribe(self, event_type: Type[Event], handler: Callable):
        """Регистрируем слушателя для конкретного события"""
        self._subscribers.setdefault(event_type, []).append(handler)
        log.debug(
            f"Подписан обработчик {handler.__name__} на событие {event_type.__name__}"
        )

    async def publish(self, event: Event):
        """Публикуем событие всем подписчикам"""
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])

        for handler in handlers:
            await handler(event)
