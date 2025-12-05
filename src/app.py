# src/app.py
import json
from pathlib import Path
from .order_service import OrdersProcessor, OrderData

FALLBACK_SAMPLE_ORDERS: list[OrderData] = [
    {"id": 1, "amount": 100, "priority": False},
    {"id": 2, "amount": 50, "priority": True},
    {"id": 3, "amount": 0},
]

SAMPLE_DATA_DIR = "data"
SAMPLE_DATA_FILENAME = "sample_orders.json"


def load_data(file_path: Path) -> list[OrderData]:
    if not file_path.exists():
        print("Warning sample data file not found. Using the fallback sample data")
        return FALLBACK_SAMPLE_ORDERS

    try:
        data = file_path.read_text(encoding="utf-8")
        sample_orders_data = json.loads(data)

        if not isinstance(sample_orders_data, list):
            raise TypeError("The file doesn't contain a valid order list")

        return sample_orders_data
    except json.JSONDecodeError:
        print(
            "The sample orders file contains a non valid JSON. Using the fallback sample data "
        )
        return FALLBACK_SAMPLE_ORDERS
    except TypeError:
        print("Validation error. Using the fallback sample data ")
        return FALLBACK_SAMPLE_ORDERS
    except Exception as e:
        print(f"Unexpected error {e}. Using the fallback sample data ")
        return FALLBACK_SAMPLE_ORDERS


def main():
    base_dir = Path(__file__).resolve().parent.parent
    sample_path = base_dir.joinpath(SAMPLE_DATA_DIR).joinpath(SAMPLE_DATA_FILENAME)

    orders_list = load_data(sample_path)
    
    result = OrdersProcessor.process_orders(orders_list)
    serializable_result = [order.__dict__ for order in result]
    print(json.dumps(serializable_result, indent=2))

if __name__ == "__main__":
    main()
