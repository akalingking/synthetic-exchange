from collections import namedtuple
from functools import total_ordering
from typing import Dict, List, Optional
from synthetic_exchange.experimental.dtype import EventType, OrderBookRow


@total_ordering
class OrderBookMessage(namedtuple("_OrderBookMessage", "type, content, timestamp")):
    type: EventType
    content: Dict[str, any]
    timestamp: float

    def __new__(
        cls,
        message_type: EventType,
        content: Dict[str, any],
        timestamp: Optional[float] = None,
        *args,
        **kwargs,
    ):
        return super(OrderBookMessage, cls).__new__(cls, message_type, content, timestamp, *args, **kwargs)

    @property
    def update_id(self) -> int:
        if self.type in [EventType.EventType_Diff, EventType.EventType_Snapshot]:
            return int(self.content["update_id"])
        else:
            return -1

    @property
    def first_update_id(self) -> int:
        if self.type is EventType.EventType_Diff:
            return self.content.get("first_update_id", self.update_id)
        else:
            return -1

    @property
    def trade_id(self) -> int:
        if self.type is EventType.EventType_Trade:
            return self.content["trade_id"]
        return -1

    @property
    def trading_pair(self) -> str:
        return self.content["trading_pair"]

    @property
    def asks(self) -> List[OrderBookRow]:
        return [
            OrderBookRow(float(price), float(amount), self.update_id) for price, amount, *trash in self.content["asks"]
        ]

    @property
    def bids(self) -> List[OrderBookRow]:
        return [
            OrderBookRow(float(price), float(amount), self.update_id) for price, amount, *trash in self.content["bids"]
        ]

    @property
    def has_update_id(self) -> bool:
        return self.type in {EventType.EventType_Diff, EventType.EventType_Snapshot}

    @property
    def has_trade_id(self) -> bool:
        return self.type == EventType.EventType_Trade

    def __eq__(self, other: "OrderBookMessage") -> bool:
        eq = (
            (self.type == other.type)
            and (
                (self.has_update_id and (self.update_id == other.update_id))
                or (self.trade_id == other.trade_id)
            )
        )
        return eq

    def __hash__(self):
        return hash(self.type, self.update_id, self.trade_id)

    def __lt__(self, other: "OrderBookMessage") -> bool:
        eq = (
            (self.has_update_id and other.has_update_id and self.update_id < other.update_id)
            or (self.has_trade_id and other.has_trade_id and self.trade_id < other.trade_id)
            or (
                ((self.timestamp != other.timestamp) and self.timestamp < other.timestamp)
                or self.has_update_id  # if same timestamp, order book messages < trade messages.
            )
        )
        return eq
