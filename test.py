# test_prices.py
from src.tools.menu_tool import get_item, get_combo

DATA = "data/mock_data.json"

# Test giá từng món
items = get_item(DATA)  # lấy tất cả
print("=== ITEM PRICES ===")
for it in items["items"]:
    print(f"{it['id']} | {it['name_vi']} | {it['price']} VND")

# Test giá 1 combo
combo = get_combo(DATA, combo_id="C001")
print("\n=== COMBO PRICE ===")
if combo["combos"]:
    c = combo["combos"][0]
    print(f"{c['id']} | {c['name_vi']} | {c['combo_price']} VND")
else:
    print("Combo C001 not found")
