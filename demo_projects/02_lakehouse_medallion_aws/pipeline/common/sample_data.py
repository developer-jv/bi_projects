from __future__ import annotations

import csv
import io
import json
from typing import Iterable


def rows_to_csv(rows: list[dict], fieldnames: Iterable[str]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def rows_to_json(rows: list[dict]) -> bytes:
    return json.dumps(rows, ensure_ascii=True, indent=2).encode("utf-8")


def build_sample_payloads() -> dict[str, bytes]:
    customers = [
        {
            "customer_id": "C001",
            "first_name": "Ana",
            "last_name": "Lopez",
            "email": "ana@example.com",
            "phone": "+15550001",
            "country": "US",
            "created_at": "2026-05-20T10:00:00Z",
        },
        {
            "customer_id": "C002",
            "first_name": "Luis",
            "last_name": "Perez",
            "email": "luis@example.com",
            "phone": "+15550002",
            "country": "US",
            "created_at": "2026-05-20T11:00:00Z",
        },
    ]
    products = [
        {"product_id": "P001", "name": "Keyboard", "category": "Accessories", "price": 49.9},
        {"product_id": "P002", "name": "Mouse", "category": "Accessories", "price": 24.9},
    ]
    orders = [
        {"order_id": "O001", "customer_id": "C001", "order_timestamp": "2026-05-20T12:00:00Z", "status": "PAID"},
        {"order_id": "O002", "customer_id": "C002", "order_timestamp": "2026-05-20T13:00:00Z", "status": "PAID"},
    ]
    order_items = [
        {"order_id": "O001", "product_id": "P001", "quantity": 1, "unit_price": 49.9},
        {"order_id": "O002", "product_id": "P002", "quantity": 2, "unit_price": 24.9},
    ]
    return {
        "customers": rows_to_json(customers),
        "products": rows_to_csv(products, ["product_id", "name", "category", "price"]),
        "orders": rows_to_csv(orders, ["order_id", "customer_id", "order_timestamp", "status"]),
        "order_items": rows_to_csv(order_items, ["order_id", "product_id", "quantity", "unit_price"]),
    }
