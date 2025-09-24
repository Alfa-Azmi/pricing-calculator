# pricing-calculator
Pricing Engine
Main Logic Summary

The Pricing Engine calculates the best price for a product based on a hierarchy of pricing rules: CUSTOMER → TIER → GROUP → NORMAL. It filters applicable prices by product, quantity, and customer attributes, then selects the one with the highest priority and lowest value.

Features

Priority-Based Pricing: Automatically chooses the best price based on the defined priority order.

OOP Design: PricingEngine class encapsulates all logic.

Data Classes: PriceEntry represents structured price rules.

Enums: PriceType ensures consistent, self-documenting price sources.

Error Handling: PricingError raised for invalid quantities or missing products.

Unit Testing: Comprehensive pytest tests verify correctness for all precedence levels and error scenarios.

Priority Order

CUSTOMER – specific to a customer ID (highest priority)

TIER – based on customer tier

GROUP – based on customer group

NORMAL – default price

Flow Diagram
   ┌───────────────────────────┐
   │ Start: Input product_id,  │
   │ quantity, customer_id     │
   └─────────────┬─────────────┘
                 │
                 ▼
   ┌───────────────────────────┐
   │ Normalize product_id to   │
   │ canonical P### format     │
   └─────────────┬─────────────┘
                 │
                 ▼
   ┌───────────────────────────┐
   │ Filter applicable prices: │
   │ product match & min_qty   │
   │ match & source/customer   │
   └─────────────┬─────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ Applicable list │
        │ empty?         │
        └─────┬──────────┘
              │ Yes → Raise PricingError
              │
              ▼ No
   ┌───────────────────────────┐
   │ Sort by priority (CUSTOMER│
   │ > TIER > GROUP > NORMAL)  │
   │ and price (lowest first)  │
   └─────────────┬─────────────┘
                 │
                 ▼
   ┌───────────────────────────┐
   │ Return best price with    │
   │ product_id, price,        │
   │ price_type                │
   └───────────────────────────┘

Running Unit Tests

To run the unit tests:

# Navigate to the project folder
cd pricing-calculator

# Run pytest to execute tests
pytest test_pricing_engine.py

Concepts Used

Filtering & Sorting: Determines applicable prices and selects the optimal one.

Type Safety & Consistency: Using Enums and typed dataclasses.

Error Handling: Robust handling of invalid inputs.

OOP: Encapsulation of logic in classes with clear responsibilities.