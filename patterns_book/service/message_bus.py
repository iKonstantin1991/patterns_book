import abc
from typing import TYPE_CHECKING, Any

from patterns_book.adapters import email
from patterns_book.domain import events

if TYPE_CHECKING:
    from collections.abc import Callable


class AbstractMessageBus(abc.ABC):
    @abc.abstractmethod
    def handle(self, event: events.Event) -> None: ...


class InMemoryMessageBus(AbstractMessageBus):
    def __init__(self) -> None:
        self.handlers: dict[type[events.Event], list[Callable[[Any], None]]] = {
            events.OutOfStock: [self._send_out_of_stock_notification],
        }

    def handle(self, event: events.Event) -> None:
        for handler in self.handlers[type(event)]:
            handler(event)

    @staticmethod
    def _send_out_of_stock_notification(event: events.OutOfStock) -> None:
        email.send_mail(
            "stock@made.com",
            f"Out of stock for {event.sku}",
        )
