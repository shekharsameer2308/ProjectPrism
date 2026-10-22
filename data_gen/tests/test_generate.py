"""
data_gen/tests/test_generate.py
Verification tests for synthetic data generation and planted margin leak.
"""

import os

import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")


@pytest.fixture(scope="module")
def raw_datasets():
    """Loads all generated raw datasets from data/raw/."""
    tables = [
        "raw_products",
        "raw_ad_spend",
        "raw_customers",
        "raw_orders",
        "raw_order_items",
        "raw_touchpoints",
        "raw_returns",
    ]
    data = {}
    for t in tables:
        csv_file = os.path.join(RAW_DATA_DIR, f"{t}.csv")
        assert os.path.exists(csv_file), f"Expected raw dataset file {csv_file} does not exist. Run 'make generate' first."
        data[t] = pd.read_csv(csv_file)
    return data


def test_row_counts_and_non_empty(raw_datasets):
    """Assert all 7 raw tables exist and contain substantial realistic volume."""
    expected_tables = [
        "raw_products",
        "raw_ad_spend",
        "raw_customers",
        "raw_orders",
        "raw_order_items",
        "raw_touchpoints",
        "raw_returns",
    ]
    for table_name in expected_tables:
        df = raw_datasets[table_name]
        assert not df.empty, f"Table {table_name} is unexpectedly empty."
        assert len(df) > 0, f"Table {table_name} has 0 rows."

    # Minimum threshold checks for 24 months
    assert len(raw_datasets["raw_products"]) >= 15, "Expected at least 15 product SKUs"
    assert len(raw_datasets["raw_ad_spend"]) >= 7000, "Expected at least 7,000 ad spend records (731 days x 10 campaigns)"
    assert len(raw_datasets["raw_orders"]) >= 80000, "Expected at least 80,000 orders over 24 months"
    assert len(raw_datasets["raw_customers"]) >= 50000, "Expected at least 50,000 customers"
    assert len(raw_datasets["raw_touchpoints"]) >= 100000, "Expected at least 100,000 touchpoints"
    assert len(raw_datasets["raw_returns"]) >= 5000, "Expected at least 5,000 returns"


def test_no_negative_prices_or_costs(raw_datasets):
    """Assert strict financial sanity: no negative prices, cogs, discounts, or revenues."""
    products = raw_datasets["raw_products"]
    assert (products["list_price"] > 0).all(), "Found non-positive list prices in raw_products"
    assert (products["unit_cogs"] > 0).all(), "Found non-positive unit COGS in raw_products"

    orders = raw_datasets["raw_orders"]
    assert (orders["gross_revenue"] >= 0).all(), "Found negative gross revenue in raw_orders"
    assert (orders["discount"] >= 0).all(), "Found negative discount in raw_orders"
    assert (orders["shipping_cost"] >= 0).all(), "Found negative shipping cost in raw_orders"
    assert (orders["payment_fee"] >= 0).all(), "Found negative payment fee in raw_orders"

    order_items = raw_datasets["raw_order_items"]
    assert (order_items["qty"] > 0).all(), "Found non-positive quantity in raw_order_items"
    assert (order_items["unit_price"] > 0).all(), "Found non-positive unit price in raw_order_items"
    assert (order_items["unit_cogs"] > 0).all(), "Found non-positive unit COGS in raw_order_items"

    returns = raw_datasets["raw_returns"]
    assert (returns["refund_amount"] > 0).all(), "Found non-positive refund amount in raw_returns"


def test_annual_spend_scale(raw_datasets):
    """Assert total spend across all channels totals approximately $40M/year (~$80M over 24 months)."""
    ad_spend = raw_datasets["raw_ad_spend"]
    total_spend = ad_spend["spend"].sum()
    # 2 years = $80M target, allowing realistic +/- 8% variance for seasonality and noise
    assert 72_000_000 <= total_spend <= 88_000_000, (
        f"Total 2-year spend ${total_spend:,.2f} is outside the expected $72M - $88M range."
    )


def test_planted_leak_exists(raw_datasets):
    """
    Verify the planted revenue leak:
    Meta_Prospecting_BroadDeal campaign:
    1. Platform reported ROAS is high (~4.0x) giving an illusion of efficiency.
    2. True contribution margin on associated orders is negative or CM-ROAS < 1.0.
    """
    ad_spend = raw_datasets["raw_ad_spend"]
    leak_spend_df = ad_spend[ad_spend["campaign_name"] == "Meta_Prospecting_BroadDeal"]
    assert not leak_spend_df.empty, "Planted leak campaign Meta_Prospecting_BroadDeal not found in ad spend."

    campaign_spend = leak_spend_df["spend"].sum()
    platform_reported_rev = leak_spend_df["platform_reported_revenue"].sum()
    platform_roas = platform_reported_rev / campaign_spend

    # 1. Platform ROAS must look attractive (> 3.5x)
    assert platform_roas >= 3.5, f"Expected platform ROAS >= 3.5, got {platform_roas:.2f}"

    # 2. Join touchpoints, orders, items, and returns to verify actual contribution margin
    touchpoints = raw_datasets["raw_touchpoints"]
    orders = raw_datasets["raw_orders"]
    order_items = raw_datasets["raw_order_items"]
    returns = raw_datasets["raw_returns"]

    # Identify orders directly acquired / touched by the leak campaign
    leak_touches = touchpoints[touchpoints["campaign_id"] == "CMP-META-01"]
    leak_cust_ids = set(leak_touches["customer_id"].dropna().unique())

    leak_orders = orders[orders["customer_id"].isin(leak_cust_ids)]
    assert not leak_orders.empty, "No orders found associated with leak campaign customers."

    # Compute order economics
    leak_order_ids = set(leak_orders["order_id"].unique())
    items_for_leak = order_items[order_items["order_id"].isin(leak_order_ids)]
    returns_for_leak = returns[returns["order_id"].isin(leak_order_ids)]

    gross_rev = leak_orders["gross_revenue"].sum()
    discounts = leak_orders["discount"].sum()
    refunds = returns_for_leak["refund_amount"].sum()
    cogs = (items_for_leak["unit_cogs"] * items_for_leak["qty"]).sum()
    shipping_cost = leak_orders["shipping_cost"].sum()
    payment_fees = leak_orders["payment_fee"].sum()

    net_rev = gross_rev - discounts - refunds
    contribution_margin = net_rev - cogs - shipping_cost - payment_fees
    cm_roas = contribution_margin / campaign_spend

    # The planted leak MUST produce a negative or sub-1.0 CM-ROAS (destroying profit)
    assert cm_roas < 1.0, (
        f"Planted leak failed: CM-ROAS is {cm_roas:.2f}, expected < 1.0 (Negative or unprofitable margin)"
    )


def test_realistic_noise_presence(raw_datasets):
    """Verify that ~2% duplicates and ~1% null campaign IDs exist to test dbt quality checks."""
    orders = raw_datasets["raw_orders"]
    touchpoints = raw_datasets["raw_touchpoints"]
    ad_spend = raw_datasets["raw_ad_spend"]

    # Duplicates in orders
    order_dups = orders.duplicated(subset=["order_id"]).sum()
    dup_pct = order_dups / len(orders)
    assert dup_pct > 0.005, f"Expected > 0.5% duplicate orders to test deduplication, got {dup_pct:.3%}"

    # Null campaign IDs in touchpoints or ad_spend
    null_tp_camps = touchpoints["campaign_id"].isna().sum()
    null_spend_camps = ad_spend["campaign_id"].isna().sum()
    assert (null_tp_camps + null_spend_camps) > 0, "Expected null campaign IDs to test 'unattributed' dbt mapping"
