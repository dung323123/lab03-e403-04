import os
import json
from typing import List, Dict, Any

def _load_data() -> Dict[str, Any]:
    """Helper to load mock data from data/mock_data.json relative to the project root."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # src/tools -> src -> root
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    data_path = os.path.join(root_dir, "data", "mock_data.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading mock data: {e}")
        return {}

DATA = _load_data()

def get_all_items() -> dict:
    """Get all item details from the menu."""
    return DATA.get("items", {})

def get_item(name: str) -> dict:
    """Get item details by name from the menu."""
    items = DATA.get("items", [])
    for item in items:
        if name.lower() in item.get("name_vi", "").lower():
            return item
    return {"error": f"Item '{name}' not found."}

def get_best_seller() -> dict:
    """Get the current best seller item information."""
    return DATA.get("best_seller", {})

def get_discount(code: str) -> dict:
    """Get discount details by its coupon code."""
    discounts = DATA.get("discounts", [])
    for discount in discounts:
        if discount.get("code", "").lower() == code.lower():
            return discount
    return {"error": f"Discount code '{code}' not found."}

def get_combo(name: str) -> dict:
    """Get combo details by its name."""
    combos = DATA.get("combos", [])
    for combo in combos:
        if name.lower() in combo.get("name_vi", "").lower():
            return combo
    return {"error": f"Combo '{name}' not found."}

tools = [
    {
        "name": "get_all_items",
        "description": "Get all item details from the menu.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_item",
        "description": "Get item details by name from the menu. Returns price, availability, and description.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The name of the item to look up (e.g., 'Gà rán')"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_best_seller",
        "description": "Get the current best-selling item information, including its name and the reason for its popularity.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_discount",
        "description": "Get discount details by its coupon code. Returns the percentage/value, minimum order requirements, and whether it's active.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The discount coupon code (e.g., 'GA20')"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "get_combo",
        "description": "Get combo details by its name. Returns the items included in the combo and its special price.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The name of the combo (e.g., 'Combo Gia đình')"}
            },
            "required": ["name"]
        }
    }
]