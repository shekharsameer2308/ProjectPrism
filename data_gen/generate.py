"""
data_gen/generate.py
Synthetic omnichannel marketing, customer transaction, and touchpoint data generator.

Client: GlobalRetail Co. ($40M annual acquisition spend)
Planted Leak: Meta_Prospecting_BroadDeal shows ~4.0x platform ROAS but negative contribution margin.
Seed: 42 (Reproducible generation)
"""

import hashlib
import os
import random
from datetime import timedelta

import numpy as np
import pandas as pd
import yaml

# Base project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")


def load_config(config_path: str = CONFIG_PATH) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)


# ------------------------------------------------------------------------------
# 1. Product Catalog Generator
# ------------------------------------------------------------------------------
def generate_products() -> pd.DataFrame:
    """
    Generates 20 SKUs across 4 categories:
    - Normal / Premium SKUs: healthy gross margin (30-40% COGS ratio).
    - Clearance / Promo SKUs (SKU-CLR-*): low list price, high COGS ratio (65-75%),
      heavily bought by the planted leak campaign (Meta_Prospecting_BroadDeal).
    """
    products = [
        # Apparel (Hero & Standard)
        {"sku": "SKU-APP-001", "category": "Apparel", "list_price": 89.00, "unit_cogs": 31.15},
        {"sku": "SKU-APP-002", "category": "Apparel", "list_price": 120.00, "unit_cogs": 42.00},
        {"sku": "SKU-APP-003", "category": "Apparel", "list_price": 65.00, "unit_cogs": 22.75},
        {"sku": "SKU-APP-004", "category": "Apparel", "list_price": 150.00, "unit_cogs": 52.50},
        {"sku": "SKU-APP-005", "category": "Apparel", "list_price": 45.00, "unit_cogs": 15.75},
        # Footwear
        {"sku": "SKU-FTW-001", "category": "Footwear", "list_price": 140.00, "unit_cogs": 49.00},
        {"sku": "SKU-FTW-002", "category": "Footwear", "list_price": 180.00, "unit_cogs": 63.00},
        {"sku": "SKU-FTW-003", "category": "Footwear", "list_price": 95.00, "unit_cogs": 33.25},
        {"sku": "SKU-FTW-004", "category": "Footwear", "list_price": 220.00, "unit_cogs": 77.00},
        # Electronics / Audio
        {"sku": "SKU-ELE-001", "category": "Electronics", "list_price": 199.00, "unit_cogs": 79.60},
        {"sku": "SKU-ELE-002", "category": "Electronics", "list_price": 299.00, "unit_cogs": 119.60},
        {"sku": "SKU-ELE-003", "category": "Electronics", "list_price": 79.00, "unit_cogs": 31.60},
        # Accessories
        {"sku": "SKU-ACC-001", "category": "Accessories", "list_price": 40.00, "unit_cogs": 14.00},
        {"sku": "SKU-ACC-002", "category": "Accessories", "list_price": 55.00, "unit_cogs": 19.25},
        {"sku": "SKU-ACC-003", "category": "Accessories", "list_price": 30.00, "unit_cogs": 10.50},
        # Clearance / Planted Leak SKUs (Low margin, bought with deep coupons)
        {"sku": "SKU-CLR-001", "category": "Apparel", "list_price": 29.99, "unit_cogs": 21.50},
        {"sku": "SKU-CLR-002", "category": "Apparel", "list_price": 24.99, "unit_cogs": 18.20},
        {"sku": "SKU-CLR-003", "category": "Footwear", "list_price": 39.99, "unit_cogs": 29.50},
        {"sku": "SKU-CLR-004", "category": "Accessories", "list_price": 19.99, "unit_cogs": 14.80},
        {"sku": "SKU-CLR-005", "category": "Electronics", "list_price": 34.99, "unit_cogs": 26.00},
    ]
    return pd.DataFrame(products)


# ------------------------------------------------------------------------------
# 2. Daily Ad Spend Generator
# ------------------------------------------------------------------------------
def generate_ad_spend(config: dict, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Generates daily ad spend across Google, Meta, TikTok, and Programmatic Display.
    - 24 months (2024-01-01 to 2025-12-31).
    - Total spend ~ $40M/year (~$80M total).
    - Planted Leak: Meta_Prospecting_BroadDeal boasts ~4.0x platform ROAS.
    - TikTok scales up mid-period (July 2024).
    """
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    total_days = len(dates)
    annual_target = config.get("annual_spend_target", 40_000_000.0)

    # Pre-calculate seasonality weights to normalize daily spend exactly to annual_target * 2.0
    daily_weights = []
    for dt in dates:
        dow = 1.10 if dt.weekday() in (5, 6) else 0.96
        is_q4 = (dt.month == 11 and dt.day >= 15) or (dt.month == 12 and dt.day <= 25)
        season = 1.95 if is_q4 else 1.0
        daily_weights.append(dow * season)
    avg_weight = float(np.mean(daily_weights))
    base_daily_spend = (annual_target * 2.0) / (total_days * avg_weight)

    # Campaign Metadata mapping
    campaign_defs = [
        # Google Ads (weight 0.38)
        {"platform": "Google Ads", "campaign_id": "CMP-GOOG-01", "campaign_name": "Google_Search_Brand", "spend_share": 0.38 * 0.25, "cpc": 1.20, "cvr": 0.085, "plat_roas": 5.5},
        {"platform": "Google Ads", "campaign_id": "CMP-GOOG-02", "campaign_name": "Google_Search_NonBrand_Generic", "spend_share": 0.38 * 0.50, "cpc": 2.80, "cvr": 0.032, "plat_roas": 2.8},
        {"platform": "Google Ads", "campaign_id": "CMP-GOOG-03", "campaign_name": "Google_Shopping_PMax", "spend_share": 0.38 * 0.25, "cpc": 1.50, "cvr": 0.040, "plat_roas": 3.2},
        # Meta Ads (weight 0.35)
        {"platform": "Meta Ads", "campaign_id": "CMP-META-01", "campaign_name": "Meta_Prospecting_BroadDeal", "spend_share": 0.35 * 0.45, "cpc": 0.55, "cvr": 0.048, "plat_roas": 4.1},
        {"platform": "Meta Ads", "campaign_id": "CMP-META-02", "campaign_name": "Meta_Prospecting_Lookalike", "spend_share": 0.35 * 0.35, "cpc": 1.10, "cvr": 0.030, "plat_roas": 2.6},
        {"platform": "Meta Ads", "campaign_id": "CMP-META-03", "campaign_name": "Meta_Retargeting_DABA", "spend_share": 0.35 * 0.20, "cpc": 1.80, "cvr": 0.065, "plat_roas": 4.5},
        # TikTok Ads (weight 0.17)
        {"platform": "TikTok Ads", "campaign_id": "CMP-TIK-01", "campaign_name": "TikTok_Spark_TopFunnel", "spend_share": 0.17 * 0.70, "cpc": 0.45, "cvr": 0.015, "plat_roas": 1.4},
        {"platform": "TikTok Ads", "campaign_id": "CMP-TIK-02", "campaign_name": "TikTok_InFeed_Catalog", "spend_share": 0.17 * 0.30, "cpc": 0.75, "cvr": 0.022, "plat_roas": 2.1},
        # Programmatic Display (weight 0.10)
        {"platform": "Programmatic Display", "campaign_id": "CMP-PROG-01", "campaign_name": "Display_Prospecting_Contextual", "spend_share": 0.10 * 0.60, "cpc": 0.90, "cvr": 0.008, "plat_roas": 0.9},
        {"platform": "Programmatic Display", "campaign_id": "CMP-PROG-02", "campaign_name": "Display_Retargeting_Dynamic", "spend_share": 0.10 * 0.40, "cpc": 1.60, "cvr": 0.025, "plat_roas": 2.4},
    ]

    records = []
    scale_up_dt = pd.Timestamp("2024-07-01")

    for dt in dates:
        # Seasonality factors
        # 1. Day of week: weekend slight bump (+10%)
        dow_factor = 1.10 if dt.weekday() in (5, 6) else 0.96
        # 2. Q4 Holiday peak: Nov 15 to Dec 25 (+80% to +120%)
        is_q4_peak = (dt.month == 11 and dt.day >= 15) or (dt.month == 12 and dt.day <= 25)
        season_factor = 1.95 if is_q4_peak else 1.0

        daily_budget = base_daily_spend * dow_factor * season_factor

        for cmp in campaign_defs:
            share = cmp["spend_share"]
            # TikTok mid-period scale up
            if cmp["platform"] == "TikTok Ads":
                share = share * 0.6 if dt < scale_up_dt else share * 1.35

            noise_factor = np.random.uniform(0.92, 1.08)
            spend = round(daily_budget * share * noise_factor, 2)
            cpc = cmp["cpc"] * np.random.uniform(0.95, 1.05)
            clicks = max(1, round(spend / cpc))
            # CTR ~ 1.5% - 3.5%
            ctr = np.random.uniform(0.015, 0.035)
            impressions = round(clicks / ctr)

            # Platform reported conversions & revenue (inflated due to self-attribution)
            cvr = cmp["cvr"] * np.random.uniform(0.92, 1.08)
            plat_convs = max(0, round(clicks * cvr))
            plat_roas = cmp["plat_roas"] * np.random.uniform(0.95, 1.05)
            plat_revenue = round(spend * plat_roas, 2)

            records.append({
                "date": dt.strftime("%Y-%m-%d"),
                "platform": cmp["platform"],
                "campaign_id": cmp["campaign_id"],
                "campaign_name": cmp["campaign_name"],
                "impressions": impressions,
                "clicks": clicks,
                "spend": spend,
                "platform_reported_conversions": plat_convs,
                "platform_reported_revenue": plat_revenue,
            })

    df = pd.DataFrame(records)
    return df


# ------------------------------------------------------------------------------
# 3. Customer, Order, Item, Touchpoint & Return Generator
# ------------------------------------------------------------------------------
def generate_customer_journey_and_orders(
    ad_spend_df: pd.DataFrame,
    products_df: pd.DataFrame,
    config: dict,
    start_date: str,
    end_date: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generates realistic customer journeys (touchpoints) and resulting transactions:
    - Multi-touch attribution touchpoints prior to orders.
    - Orders, line items, and returns.
    - Planted leak logic for Meta_Prospecting_BroadDeal:
      Deep discounts (35%), clearance SKUs (high COGS ratio), free shipping, and high returns (28%).
    """
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    regions = ["US-East", "US-West", "US-Central", "US-South", "Canada"]
    region_weights = [0.35, 0.25, 0.20, 0.15, 0.05]

    # Pre-sort products
    clearance_skus = products_df[products_df["sku"].str.startswith("SKU-CLR")].to_dict("records")
    standard_skus = products_df[~products_df["sku"].str.startswith("SKU-CLR")].to_dict("records")

    campaign_lookup = {
        "Google_Search_Brand": {"platform": "Google Ads", "id": "CMP-GOOG-01"},
        "Google_Search_NonBrand_Generic": {"platform": "Google Ads", "id": "CMP-GOOG-02"},
        "Google_Shopping_PMax": {"platform": "Google Ads", "id": "CMP-GOOG-03"},
        "Meta_Prospecting_BroadDeal": {"platform": "Meta Ads", "id": "CMP-META-01"},
        "Meta_Prospecting_Lookalike": {"platform": "Meta Ads", "id": "CMP-META-02"},
        "Meta_Retargeting_DABA": {"platform": "Meta Ads", "id": "CMP-META-03"},
        "TikTok_Spark_TopFunnel": {"platform": "TikTok Ads", "id": "CMP-TIK-01"},
        "TikTok_InFeed_Catalog": {"platform": "TikTok Ads", "id": "CMP-TIK-02"},
        "Display_Prospecting_Contextual": {"platform": "Programmatic Display", "id": "CMP-PROG-01"},
        "Display_Retargeting_Dynamic": {"platform": "Programmatic Display", "id": "CMP-PROG-02"},
    }

    customers_list = []
    orders_list = []
    order_items_list = []
    touchpoints_list = []
    returns_list = []

    cust_counter = 1
    order_counter = 1
    touch_counter = 1

    # Active customer pool for repeat orders
    # Key: customer_id -> dict(acquisition_campaign, first_order_date, repeat_propensity)
    customer_pool = {}

    for current_dt in dates:
        # Determine number of new customer orders today
        is_q4_peak = (current_dt.month == 11 and current_dt.day >= 15) or (current_dt.month == 12 and current_dt.day <= 25)
        dow_factor = 1.15 if current_dt.weekday() in (5, 6) else 0.95
        daily_new_orders_target = round(140 * dow_factor * (1.9 if is_q4_peak else 1.0))

        # 1. New Customer Acquisitions
        for _ in range(daily_new_orders_target):
            cust_id = f"CUST-{cust_counter:07d}"
            order_id = f"ORD-{order_counter:08d}"
            cust_counter += 1
            order_counter += 1

            region = random.choices(regions, weights=region_weights)[0]
            email_hash = hashlib.sha256(f"{cust_id}@clientretail.com".encode()).hexdigest()

            # Random order hour in day
            order_hour = random.randint(8, 23)
            order_minute = random.randint(0, 59)
            order_second = random.randint(0, 59)
            order_ts = current_dt.replace(hour=order_hour, minute=order_minute, second=order_second)

            # Assign Primary Acquisition Channel
            channel_rand = random.random()
            if channel_rand < 0.22:
                # Meta BroadDeal (The planted leak)
                acq_campaign = "Meta_Prospecting_BroadDeal"
                journey_type = "leak_deal"
            elif channel_rand < 0.42:
                acq_campaign = "Google_Search_NonBrand_Generic"
                journey_type = "high_intent_search"
            elif channel_rand < 0.58:
                acq_campaign = "Meta_Prospecting_Lookalike"
                journey_type = "social_discovery"
            elif channel_rand < 0.73:
                acq_campaign = "Google_Shopping_PMax"
                journey_type = "shopping"
            elif channel_rand < 0.88:
                # TikTok assisted conversion
                acq_campaign = "TikTok_Spark_TopFunnel"
                journey_type = "tiktok_assisted"
            elif channel_rand < 0.95:
                acq_campaign = "Google_Search_Brand"
                journey_type = "brand_direct"
            else:
                acq_campaign = "Display_Prospecting_Contextual"
                journey_type = "display_assisted"

            # Create Touchpoint Journey within 30 days lookback
            touches = []
            if journey_type == "leak_deal":
                # Single or short direct deal click (no assist needed)
                t_dt = order_ts - timedelta(hours=random.randint(1, 12))
                touches.append({
                    "touch_id": f"TCH-{touch_counter:09d}",
                    "customer_id": cust_id,
                    "touch_ts": t_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "platform": campaign_lookup[acq_campaign]["platform"],
                    "campaign_id": campaign_lookup[acq_campaign]["id"],
                    "touch_type": "click",
                })
                touch_counter += 1

            elif journey_type == "tiktok_assisted":
                # TikTok Top Funnel impression/click 12-25 days ago -> Google Brand search at conversion
                t1_dt = order_ts - timedelta(days=random.randint(10, 24), hours=random.randint(1, 10))
                touches.append({
                    "touch_id": f"TCH-{touch_counter:09d}",
                    "customer_id": cust_id,
                    "touch_ts": t1_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "platform": "TikTok Ads",
                    "campaign_id": "CMP-TIK-01",
                    "touch_type": "impression" if random.random() < 0.4 else "click",
                })
                touch_counter += 1

                if random.random() < 0.6:
                    t2_dt = order_ts - timedelta(days=random.randint(2, 7))
                    touches.append({
                        "touch_id": f"TCH-{touch_counter:09d}",
                        "customer_id": cust_id,
                        "touch_ts": t2_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "platform": "Meta Ads",
                        "campaign_id": "CMP-META-03",
                        "touch_type": "click",
                    })
                    touch_counter += 1

                # Last touch: Google Brand Search
                t3_dt = order_ts - timedelta(hours=random.randint(1, 4))
                touches.append({
                    "touch_id": f"TCH-{touch_counter:09d}",
                    "customer_id": cust_id,
                    "touch_ts": t3_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "platform": "Google Ads",
                    "campaign_id": "CMP-GOOG-01",
                    "touch_type": "click",
                })
                touch_counter += 1

            elif journey_type == "display_assisted":
                # Display impression -> Nonbrand or retargeting click
                t1_dt = order_ts - timedelta(days=random.randint(5, 18))
                touches.append({
                    "touch_id": f"TCH-{touch_counter:09d}",
                    "customer_id": cust_id,
                    "touch_ts": t1_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "platform": "Programmatic Display",
                    "campaign_id": "CMP-PROG-01",
                    "touch_type": "impression",
                })
                touch_counter += 1

                t2_dt = order_ts - timedelta(hours=random.randint(2, 18))
                touches.append({
                    "touch_id": f"TCH-{touch_counter:09d}",
                    "customer_id": cust_id,
                    "touch_ts": t2_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "platform": "Google Ads",
                    "campaign_id": "CMP-GOOG-02",
                    "touch_type": "click",
                })
                touch_counter += 1

            else:
                # Typical multi-touch: First touch discovery -> retargeting / search conversion
                t1_dt = order_ts - timedelta(days=random.randint(3, 14))
                touches.append({
                    "touch_id": f"TCH-{touch_counter:09d}",
                    "customer_id": cust_id,
                    "touch_ts": t1_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "platform": campaign_lookup[acq_campaign]["platform"],
                    "campaign_id": campaign_lookup[acq_campaign]["id"],
                    "touch_type": "click",
                })
                touch_counter += 1

                if random.random() < 0.45:
                    t2_dt = order_ts - timedelta(hours=random.randint(1, 6))
                    touches.append({
                        "touch_id": f"TCH-{touch_counter:09d}",
                        "customer_id": cust_id,
                        "touch_ts": t2_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "platform": "Google Ads",
                        "campaign_id": "CMP-GOOG-01",
                        "touch_type": "click",
                    })
                    touch_counter += 1

            touchpoints_list.extend(touches)

            # Generate Items & Economics for this order
            if acq_campaign == "Meta_Prospecting_BroadDeal":
                # Planted Leak: Purchases cheap clearance items, high return rate, deep coupon
                num_items = random.choices([1, 2, 3], weights=[0.60, 0.30, 0.10])[0]
                selected_skus = random.choices(clearance_skus, k=num_items)
                discount_pct = np.random.uniform(0.30, 0.45) # 30% to 45% coupon discount
                is_free_shipping = True
                return_prob = 0.28
                repeat_propensity = 0.03 # Very low retention for deal chasers
            else:
                num_items = random.choices([1, 2, 3, 4], weights=[0.45, 0.35, 0.15, 0.05])[0]
                selected_skus = random.choices(standard_skus, k=num_items)
                discount_pct = np.random.uniform(0.05, 0.15) if random.random() < 0.35 else 0.0
                is_free_shipping = random.random() < 0.65
                return_prob = 0.08
                repeat_propensity = 0.24 if "NonBrand" in acq_campaign or "Brand" in acq_campaign else 0.14

            order_gross = 0.0
            order_cogs = 0.0
            items_for_order = []

            for item_sku in selected_skus:
                qty = 1 if random.random() < 0.85 else 2
                u_price = item_sku["list_price"]
                u_cogs = item_sku["unit_cogs"]
                order_gross += round(u_price * qty, 2)
                order_cogs += round(u_cogs * qty, 2)
                items_for_order.append({
                    "order_id": order_id,
                    "sku": item_sku["sku"],
                    "qty": qty,
                    "unit_price": u_price,
                    "unit_cogs": u_cogs,
                })

            order_items_list.extend(items_for_order)

            discount_amt = round(order_gross * discount_pct, 2)
            shipping_charged = 0.0 if is_free_shipping else 8.50
            shipping_cost = round(np.random.uniform(7.50, 11.00), 2)
            tax_amt = round((order_gross - discount_amt) * 0.075, 2)
            # Payment processing fee: 2.9% + $0.30
            payment_fee = round((order_gross - discount_amt + shipping_charged + tax_amt) * 0.029 + 0.30, 2)

            orders_list.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_ts": order_ts.strftime("%Y-%m-%d %H:%M:%S"),
                "gross_revenue": order_gross,
                "discount": discount_amt,
                "shipping_charged": shipping_charged,
                "shipping_cost": shipping_cost,
                "payment_fee": payment_fee,
                "tax": tax_amt,
                "status": "completed",
            })

            # Check for return
            if random.random() < return_prob:
                returned_item = random.choice(items_for_order)
                return_days = random.randint(3, 14)
                return_ts = order_ts + timedelta(days=return_days, hours=random.randint(1, 10))
                if return_ts.date() <= dates[-1].date():
                    # Refund amount is item gross minus proportional discount
                    refund_val = round((returned_item["unit_price"] * returned_item["qty"]) * (1.0 - discount_pct), 2)
                    returns_list.append({
                        "order_id": order_id,
                        "sku": returned_item["sku"],
                        "return_ts": return_ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "refund_amount": refund_val,
                    })

            customers_list.append({
                "customer_id": cust_id,
                "first_order_date": current_dt.strftime("%Y-%m-%d"),
                "region": region,
                "email_hash": email_hash,
            })

            customer_pool[cust_id] = {
                "acq_campaign": acq_campaign,
                "first_order_ts": order_ts,
                "repeat_propensity": repeat_propensity,
            }

        # 2. Repeat Customer Orders
        # Sample customers from existing pool who might repeat today
        eligible_custs = [
            cid for cid, cdata in customer_pool.items()
            if (current_dt - cdata["first_order_ts"]).days >= 20
        ]
        if eligible_custs:
            # Repeat order rate
            daily_repeats = round(len(eligible_custs) * 0.0025 * (1.8 if is_q4_peak else 1.0))
            if daily_repeats > 0:
                sampled_cids = random.sample(eligible_custs, min(daily_repeats, len(eligible_custs)))
                for rep_cid in sampled_cids:
                    cdata = customer_pool[rep_cid]
                    if random.random() > cdata["repeat_propensity"]:
                        continue

                    order_id = f"ORD-{order_counter:08d}"
                    order_counter += 1

                    rep_order_hour = random.randint(9, 22)
                    rep_order_ts = current_dt.replace(hour=rep_order_hour, minute=random.randint(0, 59), second=random.randint(0, 59))

                    # Touchpoint for repeat order: usually Brand search or direct/organic
                    touches = [{
                        "touch_id": f"TCH-{touch_counter:09d}",
                        "customer_id": rep_cid,
                        "touch_ts": (rep_order_ts - timedelta(hours=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S"),
                        "platform": "Google Ads",
                        "campaign_id": "CMP-GOOG-01",
                        "touch_type": "click",
                    }]
                    touch_counter += 1
                    touchpoints_list.extend(touches)

                    # Repeat buyers buy standard catalog items
                    num_items = random.choices([1, 2, 3], weights=[0.50, 0.35, 0.15])[0]
                    selected_skus = random.choices(standard_skus, k=num_items)
                    discount_pct = 0.05 if random.random() < 0.20 else 0.0

                    order_gross = 0.0
                    order_cogs = 0.0
                    items_for_order = []
                    for item_sku in selected_skus:
                        qty = 1 if random.random() < 0.90 else 2
                        order_gross += round(item_sku["list_price"] * qty, 2)
                        order_cogs += round(item_sku["unit_cogs"] * qty, 2)
                        items_for_order.append({
                            "order_id": order_id,
                            "sku": item_sku["sku"],
                            "qty": qty,
                            "unit_price": item_sku["list_price"],
                            "unit_cogs": item_sku["unit_cogs"],
                        })

                    order_items_list.extend(items_for_order)
                    discount_amt = round(order_gross * discount_pct, 2)
                    shipping_charged = 0.0 if random.random() < 0.70 else 8.50
                    shipping_cost = round(np.random.uniform(7.50, 10.50), 2)
                    tax_amt = round((order_gross - discount_amt) * 0.075, 2)
                    payment_fee = round((order_gross - discount_amt + shipping_charged + tax_amt) * 0.029 + 0.30, 2)

                    orders_list.append({
                        "order_id": order_id,
                        "customer_id": rep_cid,
                        "order_ts": rep_order_ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "gross_revenue": order_gross,
                        "discount": discount_amt,
                        "shipping_charged": shipping_charged,
                        "shipping_cost": shipping_cost,
                        "payment_fee": payment_fee,
                        "tax": tax_amt,
                        "status": "completed",
                    })

                    # Low return rate for repeat customers (6%)
                    if random.random() < 0.06:
                        returned_item = random.choice(items_for_order)
                        return_ts = rep_order_ts + timedelta(days=random.randint(3, 10))
                        if return_ts.date() <= dates[-1].date():
                            returns_list.append({
                                "order_id": order_id,
                                "sku": returned_item["sku"],
                                "return_ts": return_ts.strftime("%Y-%m-%d %H:%M:%S"),
                                "refund_amount": round(returned_item["unit_price"] * returned_item["qty"], 2),
                            })

    customers_df = pd.DataFrame(customers_list)
    orders_df = pd.DataFrame(orders_list)
    order_items_df = pd.DataFrame(order_items_list)
    touchpoints_df = pd.DataFrame(touchpoints_list)
    returns_df = pd.DataFrame(returns_list)

    return customers_df, orders_df, order_items_df, touchpoints_df, returns_df


# ------------------------------------------------------------------------------
# 4. Realistic Noise Injection (~2% duplicates, ~1% null campaign_id)
# ------------------------------------------------------------------------------
def inject_realistic_noise(
    ad_spend_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    touchpoints_df: pd.DataFrame,
    config: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Injects controlled noise per Section 2.2:
    - ~2% duplicate rows in orders and touchpoints (to test dbt deduplication)
    - ~1% null campaign_id in touchpoints and ad_spend (to test 'unattributed' mapping)
    """
    noise_cfg = config.get("noise", {})
    dup_rate = noise_cfg.get("duplicate_rate", 0.02)
    null_rate = noise_cfg.get("null_campaign_id_rate", 0.01)

    # 1. Duplicates
    if dup_rate > 0:
        orders_dups = orders_df.sample(frac=dup_rate, random_state=42)
        orders_df = pd.concat([orders_df, orders_dups], ignore_index=True)

        touch_dups = touchpoints_df.sample(frac=dup_rate, random_state=42)
        touchpoints_df = pd.concat([touchpoints_df, touch_dups], ignore_index=True)

    # 2. Null campaign IDs
    if null_rate > 0:
        mask_touch = np.random.rand(len(touchpoints_df)) < null_rate
        touchpoints_df.loc[mask_touch, "campaign_id"] = None

        mask_spend = np.random.rand(len(ad_spend_df)) < null_rate
        ad_spend_df.loc[mask_spend, "campaign_id"] = None

    return ad_spend_df, orders_df, touchpoints_df


# ------------------------------------------------------------------------------
# 5. Master Orchestrator
# ------------------------------------------------------------------------------
def generate_all_data(output_dir: str = OUTPUT_DIR) -> dict[str, pd.DataFrame]:
    """
    Main generator execution function:
    Creates products, ad spend, customer journeys, orders, items, returns,
    injects noise, and writes both Parquet and CSV files to data/raw/.
    """
    config = load_config()
    seed = config.get("seed", 42)
    set_seed(seed)

    start_date = config.get("start_date", "2024-01-01")
    end_date = config.get("end_date", "2025-12-31")

    print(f"--> [DataGen] Starting synthetic generation (Seed={seed}, Period: {start_date} to {end_date})")

    # 1. Products
    products_df = generate_products()
    print(f"    • Generated {len(products_df)} products")

    # 2. Ad Spend
    ad_spend_df = generate_ad_spend(config, start_date, end_date)
    total_spend = ad_spend_df["spend"].sum()
    print(f"    • Generated {len(ad_spend_df):,} daily ad spend records (Total spend: ${total_spend:,.2f})")

    # 3. Customers, Orders, Items, Touchpoints, Returns
    customers_df, orders_df, order_items_df, touchpoints_df, returns_df = (
        generate_customer_journey_and_orders(ad_spend_df, products_df, config, start_date, end_date)
    )
    print(f"    • Generated {len(customers_df):,} customers")
    print(f"    • Generated {len(orders_df):,} orders")
    print(f"    • Generated {len(order_items_df):,} order items")
    print(f"    • Generated {len(touchpoints_df):,} touchpoints")
    print(f"    • Generated {len(returns_df):,} returns")

    # 4. Inject Realistic Noise
    ad_spend_df, orders_df, touchpoints_df = inject_realistic_noise(
        ad_spend_df, orders_df, touchpoints_df, config
    )
    print(f"    • Injected noise: orders after dups={len(orders_df):,}, touchpoints after dups={len(touchpoints_df):,}")

    # 5. Persist to data/raw/
    os.makedirs(output_dir, exist_ok=True)
    datasets = {
        "raw_products": products_df,
        "raw_ad_spend": ad_spend_df,
        "raw_customers": customers_df,
        "raw_orders": orders_df,
        "raw_order_items": order_items_df,
        "raw_touchpoints": touchpoints_df,
        "raw_returns": returns_df,
    }

    for table_name, df in datasets.items():
        csv_path = os.path.join(output_dir, f"{table_name}.csv")
        parquet_path = os.path.join(output_dir, f"{table_name}.parquet")
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
        print(f"    -> Saved {table_name}: CSV ({os.path.getsize(csv_path):,} bytes), Parquet ({os.path.getsize(parquet_path):,} bytes)")

    print("--> [DataGen] Synthetic dataset generation completed successfully.")
    return datasets


if __name__ == "__main__":
    generate_all_data()
