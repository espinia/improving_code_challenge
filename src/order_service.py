# src/order_service.py
from dataclasses import dataclass
from enum import StrEnum
from typing import TypedDict, NotRequired


class OrderData(TypedDict):
    id: int
    amount: int
    priority: NotRequired[bool]


class OrderStatus(StrEnum):
    OK = "ok"
    ERROR = "error"


@dataclass
class ProcessedOrder:
    id: int
    status: OrderStatus
    priority: bool


class OrdersProcessor:
    @staticmethod
    def process_orders(
        order_list: list[OrderData],
    ) -> list[ProcessedOrder]:
        if order_list is None:
            return []

        results: list[ProcessedOrder] = []
        success_orders: list[ProcessedOrder] = []
        error_orders: list[ProcessedOrder] = []

        for order in order_list:
            order_id = order.get("id")
            amount = order.get("amount")

            if not isinstance(amount, int) or amount <= 0:
                processed_order = ProcessedOrder(
                    id=order_id, status=OrderStatus.ERROR, priority=False
                )
                error_orders.append(processed_order)
            else:
                is_priority = bool(order.get("priority") is True)
                processed_order = ProcessedOrder(
                    id=order_id, status=OrderStatus.OK, priority=is_priority
                )
                success_orders.append(processed_order)

        success_orders.sort(key=lambda order: order.priority, reverse=True)
        error_orders.sort(key=lambda order: order.priority, reverse=True)
        results = success_orders + error_orders
        return results
