import pytest
from pricing_engine import PricingEngine, PriceEntry, PriceType, PricingError

# Sample price entries
prices = [
    PriceEntry(product_id="P001", min_qty=1, price=100, source=PriceType.NORMAL),
    PriceEntry(product_id="P002", min_qty=1, price=10, source=PriceType.NORMAL),
    PriceEntry(product_id="P001", min_qty=3, price=95, source=PriceType.TIER, key="GOLD"),
    PriceEntry(product_id="P003", min_qty=2, price=50, source=PriceType.GROUP, key="GRP1"),
    PriceEntry(product_id="P002", min_qty=1, price=5, source=PriceType.CUSTOMER, key=6),
]

customer_tiers = {2: "GOLD", 6: "SILVER"}
customer_groups = {6: "GRP1"}

engine = PricingEngine(prices, customer_tiers, customer_groups)

# Correctness Tests
def test_customer_priority():
    result = engine.get_best_price(product_id=2, quantity=1, customer_id=6)
    assert result["price_type"] == "CUSTOMER"
    assert result["price"] == 5

def test_tier_priority():
    result = engine.get_best_price(product_id=1, quantity=4, customer_id=2)
    assert result["price_type"] == "TIER"
    assert result["price"] == 95

def test_group_priority():
    result = engine.get_best_price(product_id=3, quantity=2, customer_id=6)
    assert result["price_type"] == "GROUP"
    assert result["price"] == 50

def test_normal_priority():
    result = engine.get_best_price(product_id=1, quantity=1, customer_id=6)
    assert result["price_type"] == "NORMAL"
    assert result["price"] == 100

# Error Handling Tests
def test_invalid_quantity():
    with pytest.raises(PricingError) as exc_info:
        engine.get_best_price(product_id=1, quantity=0, customer_id=2)
    assert "Quantity must be greater than zero" in str(exc_info.value)

def test_missing_product():
    with pytest.raises(PricingError) as exc_info:
        engine.get_best_price(product_id=999, quantity=1, customer_id=2)
    assert "No price found" in str(exc_info.value)
