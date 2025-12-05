# tests/test_order_service.py
import pytest
from src.order_service import (
    OrdersProcessor,
    OrderData,
    OrderStatus,
    ProcessedOrder,
)

class TestOrdersProcessor:
    """
    Tests for the OrdersProcessor class, focusing on order validation and prioritization.
    """

    def test_successful_prioritization_and_status(self):
        """
        Tests that valid orders are processed correctly, assigned 'OK' status,
        and sorted correctly (priority=True first).
        """
        orders: list[OrderData] = [
            {"id": 101, "amount": 500, "priority": False},
            {"id": 102, "amount": 100, "priority": True},
            {"id": 103, "amount": 250, "priority": False},
            {"id": 104, "amount": 75, "priority": True},
        ]

        expected = [
            ProcessedOrder(id=102, status=OrderStatus.OK, priority=True),
            ProcessedOrder(id=104, status=OrderStatus.OK, priority=True),
            ProcessedOrder(id=101, status=OrderStatus.OK, priority=False),
            ProcessedOrder(id=103, status=OrderStatus.OK, priority=False),
        ]

        result = OrdersProcessor.process_orders(orders)
        assert result == expected

    def test_invalid_amount_zero(self):
        """Tests that an order with amount=0 results in an ERROR status."""
        orders: list[OrderData] = [
            {"id": 201, "amount": 0, "priority": True},
        ]

        expected = [
            # ID 201 is ERROR and priority=False.
            ProcessedOrder(id=201, status=OrderStatus.ERROR, priority=False),
        ]

        result = OrdersProcessor.process_orders(orders)
        # Note: The original code does not sort by priority for ERROR items specifically,
        # but since both have priority=False, the order is based on processing.
        assert result == expected

    def test_invalid_amount_negative(self):
        """Tests that an order with a negative amount results in an ERROR status."""
        orders: list[OrderData] = [
            {"id": 301, "amount": -10, "priority": True},
            {"id": 302, "amount": 1000, "priority": True},
        ]

        expected = [
            ProcessedOrder(id=302, status=OrderStatus.OK, priority=True),
            ProcessedOrder(id=301, status=OrderStatus.ERROR, priority=False),
        ]

        result = OrdersProcessor.process_orders(orders)
        assert result == expected

    def test_invalid_amount_non_integer(self):
        """
        Tests orders where 'amount' is not an integer (e.g., string, float, or None).
        All should result in ERROR.
        """
        orders: list[OrderData] = [
            {"id": 401, "amount": "150", "priority": False},
            {"id": 402, "amount": 50.5, "priority": True},
            {"id": 403, "amount": None, "priority": True},  # Explicitly None
            {"id": 404, "amount": 200, "priority": True},  # Control order
        ]

        expected = [
            ProcessedOrder(id=404, status=OrderStatus.OK, priority=True),
            ProcessedOrder(id=402, status=OrderStatus.ERROR, priority=False),
            ProcessedOrder(id=403, status=OrderStatus.ERROR, priority=False),
            ProcessedOrder(id=401, status=OrderStatus.ERROR, priority=False),
        ]

        result = OrdersProcessor.process_orders(orders)
        assert result[0] == expected[0]
        # Check that all invalid orders were correctly marked as ERROR
        for order in result[1:]:
            assert order.status == OrderStatus.ERROR
            assert order.priority is False

    def test_missing_amount_key(self):
        """
        Tests an edge case where the 'amount' key is missing from the order (even if TypedDict
        suggests it's required, the runtime behavior uses .get() which returns None).
        """
        orders: list[OrderData] = [
            {"id": 501, "priority": True},  # Missing amount
        ]

        expected = [
            ProcessedOrder(id=501, status=OrderStatus.ERROR, priority=False),
        ]

        result = OrdersProcessor.process_orders(orders)
        assert result == expected

    def test_missing_priority_key(self):
        """
        Tests that an order without the optional 'priority' key defaults to priority=False.
        """
        orders: list[OrderData] = [
            {"id": 601, "amount": 500},  # Missing priority
            {"id": 602, "amount": 100, "priority": True},
        ]

        expected = [
            ProcessedOrder(id=602, status=OrderStatus.OK, priority=True),
            ProcessedOrder(id=601, status=OrderStatus.OK, priority=False),
        ]

        result = OrdersProcessor.process_orders(orders)
        assert result == expected

    def test_edge_case_empty_list(self):
        """Tests processing an empty list of orders."""
        orders: list[OrderData] = []
        result = OrdersProcessor.process_orders(orders)
        assert result == []

    def test_edge_case_none_input(self):
        """Tests processing a None input, which should be gracefully handled as an empty list."""
        orders = None
        result = OrdersProcessor.process_orders(orders)
        assert result == []

    def test_mixed_valid_and_invalid_and_priority(self):
        """Tests a complex scenario with all types of orders, verifying status and sort order."""
        orders: list[OrderData] = [
            {"id": 701, "amount": 100, "priority": False},
            {"id": 702, "amount": 0, "priority": True},  # Invalid
            {"id": 703, "amount": 200},  # Valid, default False
            {"id": 704, "amount": 50, "priority": True},  # Valid, Priority
            {"id": 705, "amount": "abc", "priority": False},  # Invalid type
        ]

        result = OrdersProcessor.process_orders(orders)

        # Expected sorted order: Priority OK, then Non-Priority OK, then Errors (all priority=False)
        expected_ids_in_order = [704, 701, 702, 703, 705]

        assert len(result) == 5
        assert [r.id for r in result] == expected_ids_in_order

        # Verify statuses
        assert result[0].status == OrderStatus.OK and result[0].priority is True  # 704
        assert result[1].status == OrderStatus.OK and result[1].priority is False # 701
        assert result[2].status == OrderStatus.ERROR and result[2].priority is False # 702
        assert result[3].status == OrderStatus.OK and result[3].priority is False # 703
        assert result[4].status == OrderStatus.ERROR and result[4].priority is False # 705
