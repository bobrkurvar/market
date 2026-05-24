from typing import Callable, Dict, List, Type
import logging
from domain import Event
import asyncio

log = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._subscribers: Dict[Type[Event], List[Callable]] = {}

    def subscribe(self, event_type: Type[Event], handler: Callable):
        """Регистрируем слушателя для конкретного события"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        log.debug(f"Подписан обработчик {handler.__name__} на событие {event_type.__name__}")

    def publish(self, event: Event):
        """Публикуем событие всем подписчикам"""
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])

        for handler in handlers:
            asyncio.create_task(handler(event)),
