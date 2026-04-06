import pytest
from src.tools.restaurant_tools import (
    get_item,
    get_all_items,
    get_best_seller,
    get_best_five,
    get_combo,
    check_freeship,
    _tool_check_freeship
)

def test_get_item_valid_by_id():
    """Test retrieving a valid item by its ID."""
    result = get_item("I001")
    assert result["ok"] is True
    assert result["item"]["id"] == "I001"
    assert result["item"]["name_vi"] == "Gà rán 2 miếng"

def test_get_item_valid_by_name():
    """Test retrieving a valid item by its name (exact or case-insensitive)."""
    result = get_item("Burger gà")
    assert result["ok"] is True
    assert result["item"]["id"] == "I003"
    
    # Test without accents and lowercase
    result2 = get_item("burger ga")
    assert result2["ok"] is True
    assert result2["item"]["id"] == "I003"

def test_get_item_invalid():
    """Test retrieving a non-existent item."""
    result = get_item("I999")
    assert result["ok"] is False
    assert "not found" in result["message"]

def test_get_all_items():
    """Test retrieving all items in the menu."""
    result = get_all_items()
    assert result["ok"] is True
    assert isinstance(result["items"], list)
    assert len(result["items"]) > 0

def test_get_best_seller():
    """Test retrieving the top best-selling item."""
    result = get_best_seller()
    assert result["ok"] is True
    # The current mock data best seller is I002
    assert result["item"]["id"] == "I002"

def test_get_best_five():
    """Test retrieving the top 5 available items."""
    result = get_best_five()
    assert result["ok"] is True
    assert isinstance(result["items"], list)
    assert len(result["items"]) <= 5

def test_get_combo_valid():
    """Test retrieving a valid combo by ID or Name."""
    result = get_combo("C001")
    assert result["ok"] is True
    assert result["combo"]["id"] == "C001"
    
    # Test by alias
    result2 = get_combo("PERSONAL")
    assert result2["ok"] is True
    assert result2["combo"]["id"] == "C001"

def test_get_combo_all():
    """Test retrieving all combos when no argument is passed."""
    result = get_combo()
    assert result["ok"] is True
    assert isinstance(result["combos"], list)
    assert len(result["combos"]) > 0

def test_check_freeship_eligible_hanoi():
    """Test that checking freeship for Ha Noi with sufficient amount works."""
    result = check_freeship(250000, "Ha Noi")
    assert result["ok"] is True
    assert result["deliverable"] is True
    assert result["freeship"] is True

def test_check_freeship_ineligible_amount_hanoi():
    """Test freeship for Ha Noi with insufficient amount."""
    result = check_freeship(150000, "Hanoi")
    assert result["ok"] is True
    assert result["deliverable"] is True
    assert result["freeship"] is False
    assert result["remaining_for_freeship"] == 50000

def test_check_freeship_other_city():
    """Test that delivery is not available for cities other than Ha Noi."""
    result = check_freeship(300000, "Ho Chi Minh")
    assert result["ok"] is True
    assert result["deliverable"] is False
    assert result["freeship"] is False
    assert "only available in Ha Noi" in result["message"]

def test_tool_check_freeship_string_parsing():
    """Test the wrapper function that parses string arguments for check_freeship."""
    # Test valid combination
    result = _tool_check_freeship("250000,Ha Noi")
    assert result["ok"] is True
    assert result["freeship"] is True
    
    # Test flipped arguments
    result2 = _tool_check_freeship("Ha Noi, 150000")
    assert result2["ok"] is True
    assert result2["freeship"] is False
    assert result2["remaining_for_freeship"] == 50000
