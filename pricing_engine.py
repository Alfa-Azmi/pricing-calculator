from dataclasses import dataclass
from typing import List, Dict, Union, Optional
from enum import Enum


# Custom exception for errors
class PricingError(Exception):
    """Custom exception for pricing-related errors."""
    pass
# Enum for price source type
class PriceType(Enum):
    CUSTOMER = "CUSTOMER"  # Price specific to a customer
    TIER = "TIER"          # Price specific to a customer tier
    GROUP = "GROUP"        # Price specific to a customer group
    NORMAL = "NORMAL"      # Default/general price

# Data class to represent a single price entry
@dataclass
class PriceEntry:
    product_id: str                     # Canonical product code (e.g., "P001")
    min_qty: int                        # Minimum quantity for this price to apply
    price: float                        # Price value
    source: PriceType                    # Source/type of price (CUSTOMER/TIER/GROUP/NORMAL)
    key: Optional[Union[int, str]] = None  # Identifier: customer_id (int), tier/group (str), None for NORMAL

# Pricing engine class
class PricingEngine:
    # Priority map for price types: lower number = higher priority
    PRIORITY = {
        PriceType.CUSTOMER: 1,
        PriceType.TIER: 2,
        PriceType.GROUP: 3,
        PriceType.NORMAL: 4,
    }

    def __init__(self, prices: List[PriceEntry], customer_tiers: Dict[int, str], customer_groups: Dict[int, str]):
        """
        Initialize the pricing engine.
        :param prices: List of all PriceEntry objects
        :param customer_tiers: Mapping of customer_id -> tier name
        :param customer_groups: Mapping of customer_id -> group name
        """
        self.prices = prices
        self.customer_tiers = customer_tiers
        self.customer_groups = customer_groups

    # Helper method: normalize product_id
    @staticmethod
    def normalize_product_code(product_id: Union[int, str]) -> str:
        """
        Convert input product_id to canonical "P###" format.
        Accepts int (1 -> "P001"), string with/without 'P', or numeric string.
        Raises PricingError for invalid format.
        """
        if isinstance(product_id, int):
            return f"P{product_id:03d}"  # pad integers with zeros, e.g., 1 -> P001
        if isinstance(product_id, str) and product_id.upper().startswith("P"):
            return product_id.upper()    # already in "P###" form
        if isinstance(product_id, str) and product_id.isdigit():
            return f"P{int(product_id):03d}"  # numeric string -> P###
        raise PricingError(f"Invalid product_id: {product_id}")

    # Core method: find the best price for a given product, quantity, and customer
    def get_best_price(self, product_id: Union[int, str], quantity: int, customer_id: int) -> dict:
        """
        Determine the best applicable price for a product and customer.
        Raises PricingError if no applicable price is found or quantity is invalid.
        """
        if quantity <= 0:
            raise PricingError("Quantity must be greater than zero.")

        # Normalize product_id to P### format
        prod_code = self.normalize_product_code(product_id)

        # Get customer tier/group from mappings (if any)
        tier = self.customer_tiers.get(customer_id)
        group = self.customer_groups.get(customer_id)

        # Filter all price entries to find applicable ones
        applicable = [
            p for p in self.prices
            if p.product_id == prod_code                 # Must match product
            and quantity >= p.min_qty                    # Quantity must meet min_qty
            and (
                # Check if price is for this specific customer
                (p.source == PriceType.CUSTOMER and isinstance(p.key, int) and p.key == customer_id) or
                # Check if price is for the customer's tier
                (p.source == PriceType.TIER and isinstance(p.key, str) and p.key == tier) or
                # Check if price is for the customer's group
                (p.source == PriceType.GROUP and isinstance(p.key, str) and p.key == group) or
                # Normal price always applies if nothing else
                (p.source == PriceType.NORMAL)
            )
        ]

        # Raise error if no applicable price
        if not applicable:
            raise PricingError(f"No price found for {prod_code} with quantity {quantity}.")

        # Select the best price: prioritize by price source, then lowest price
        best = min(applicable, key=lambda p: (self.PRIORITY[p.source], p.price))

        # Return result as dict with double-quoted price_type
        return {"product_id": best.product_id, "price": best.price, "price_type": best.source.value}


# Main program to demonstrate functionality
def main():
    # Define sample prices
    prices = [
        PriceEntry(product_id="P002", min_qty=1, price=5, source=PriceType.CUSTOMER, key=6),   # Customer-specific
        PriceEntry(product_id="P001", min_qty=3, price=95, source=PriceType.TIER, key="GOLD"), # Tier-specific
        PriceEntry(product_id="P003", min_qty=2, price=50, source=PriceType.GROUP, key="GRP1"), # Group-specific
        PriceEntry(product_id="P001", min_qty=1, price=120, source=PriceType.NORMAL),           # Normal/default
        PriceEntry(product_id="P002", min_qty=1, price=10, source=PriceType.NORMAL),
    ]

    # Define customer tiers and groups
    customer_tiers = {2: "GOLD", 6: "SILVER"}   # customer_id -> tier
    customer_groups = {6: "GRP1"}               # customer_id -> group

    # Initialize the pricing engine
    engine = PricingEngine(prices, customer_tiers, customer_groups)

    # Input data: product, quantity, customer
    input_data = [
        {"product_id": 1, "quantity": 4, "customer_id": 2},  # Should pick TIER price
        {"product_id": 2, "quantity": 3, "customer_id": 6},  # Should pick CUSTOMER price
        {"product_id": 3, "quantity": 0, "customer_id": 6},  # Invalid quantity → error
        {"product_id": 5, "quantity": 2, "customer_id": 6},  # No price → error
    ]

    # Process each input row
    outputs = []
    for row in input_data:
        try:
            # Try to get best price
            result = engine.get_best_price(row["product_id"], row["quantity"], row["customer_id"])
            outputs.append(result)
        except PricingError as e:
            # On error, return normalized product_id + error message
            outputs.append({
                "product_id": PricingEngine.normalize_product_code(row["product_id"]),
                "error": str(e)
            })

    # Print all results
    print(outputs)

# Entry point
if __name__ == "__main__":
    main()
