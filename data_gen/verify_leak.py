"""
data_gen/verify_leak.py
Analytical verification script demonstrating:
1. Spend and platform ROAS by channel
2. The planted margin leak in Meta_Prospecting_BroadDeal
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")


def run_verification():
    ad_spend = pd.read_csv(os.path.join(RAW_DIR, "raw_ad_spend.csv"))
    orders = pd.read_csv(os.path.join(RAW_DIR, "raw_orders.csv")).drop_duplicates(subset=["order_id"])
    items = pd.read_csv(os.path.join(RAW_DIR, "raw_order_items.csv"))
    returns = pd.read_csv(os.path.join(RAW_DIR, "raw_returns.csv"))
    touchpoints = pd.read_csv(os.path.join(RAW_DIR, "raw_touchpoints.csv"))

    print("==========================================================================")
    print("1. SPEND & PLATFORM-REPORTED ROAS BY PLATFORM (2-YEAR TOTAL)")
    print("==========================================================================")
    plat_summary = ad_spend.groupby("platform").agg(
        total_spend=("spend", "sum"),
        reported_conversions=("platform_reported_conversions", "sum"),
        reported_revenue=("platform_reported_revenue", "sum"),
    ).reset_index()
    plat_summary["platform_roas"] = (plat_summary["reported_revenue"] / plat_summary["total_spend"]).round(2)
    plat_summary["annual_spend"] = (plat_summary["total_spend"] / 2.0).round(2)

    for _, r in plat_summary.iterrows():
        print(f"• {r['platform']:<22} | Spend: ${r['total_spend']:>12,.2f} (${r['annual_spend']:>10,.2f}/yr) | Reported ROAS: {r['platform_roas']:>4.2f}x")

    print(f"\nTOTAL ACQUISITION SPEND: ${ad_spend['spend'].sum():,.2f} (~${ad_spend['spend'].sum()/2:,.2f}/year)")

    print("\n==========================================================================")
    print("2. CAMPAIGN-LEVEL AUDIT & THE PLANTED REVENUE LEAK")
    print("==========================================================================")

    # For each campaign, compute actual economics of associated buyers
    campaigns = ad_spend.groupby(["platform", "campaign_id", "campaign_name"]).agg(
        campaign_spend=("spend", "sum"),
        platform_rev=("platform_reported_revenue", "sum"),
    ).reset_index()
    campaigns["platform_roas"] = (campaigns["platform_rev"] / campaigns["campaign_spend"]).round(2)

    # Join orders and items for item cogs
    items_cogs = items.groupby("order_id").apply(
        lambda x: (x["unit_cogs"] * x["qty"]).sum(), include_groups=False
    ).rename("total_cogs")
    order_returns = returns.groupby("order_id")["refund_amount"].sum().rename("total_refunds")

    order_econ = orders.merge(items_cogs, on="order_id", how="left").merge(order_returns, on="order_id", how="left")
    order_econ["total_cogs"] = order_econ["total_cogs"].fillna(0)
    order_econ["total_refunds"] = order_econ["total_refunds"].fillna(0)

    # Net Revenue & Contribution Margin per order
    order_econ["net_revenue"] = order_econ["gross_revenue"] - order_econ["discount"] - order_econ["total_refunds"]
    order_econ["contribution_margin"] = (
        order_econ["net_revenue"] - order_econ["total_cogs"] - order_econ["shipping_cost"] - order_econ["payment_fee"]
    )

    # Touchpoint to order mapping (Last touch)
    valid_touches = touchpoints.dropna(subset=["campaign_id"]).sort_values("touch_ts")
    last_touches = valid_touches.drop_duplicates(subset=["customer_id"], keep="last")
    order_with_camp = order_econ.merge(last_touches[["customer_id", "campaign_id"]], on="customer_id", how="inner")

    camp_margins = order_with_camp.groupby("campaign_id").agg(
        attributed_orders=("order_id", "count"),
        net_revenue=("net_revenue", "sum"),
        total_cm=("contribution_margin", "sum"),
    ).reset_index()

    audit_table = campaigns.merge(camp_margins, on="campaign_id", how="left")
    audit_table["cm_roas"] = (audit_table["total_cm"] / audit_table["campaign_spend"]).round(2)

    print(f"{'Campaign Name':<34} | {'Platform ROAS':<13} | {'CM-ROAS':<8} | {'Status'}")
    print("-" * 75)
    for _, row in audit_table.sort_values("cm_roas").iterrows():
        status = "⚠️ PROFIT LEAK (NEGATIVE CM)" if row["cm_roas"] < 1.0 else "✅ HEALTHY"
        print(f"{row['campaign_name']:<34} | {row['platform_roas']:>9.2f}x    | {row['cm_roas']:>6.2f}x  | {status}")

    print("\n==========================================================================")
    print("3. DEEP DIVE: Meta_Prospecting_BroadDeal ECONOMICS")
    print("==========================================================================")
    leak_row = audit_table[audit_table["campaign_name"] == "Meta_Prospecting_BroadDeal"].iloc[0]
    leak_orders = order_with_camp[order_with_camp["campaign_id"] == "CMP-META-01"]
    gross = leak_orders["gross_revenue"].sum()
    disc = leak_orders["discount"].sum()
    ref = leak_orders["total_refunds"].sum()
    cogs = leak_orders["total_cogs"].sum()
    ship = leak_orders["shipping_cost"].sum()
    fees = leak_orders["payment_fee"].sum()
    cm = leak_orders["contribution_margin"].sum()

    print(f"• Campaign Spend:               ${leak_row['campaign_spend']:>12,.2f}")
    print(f"• Platform Reported Revenue:    ${leak_row['platform_rev']:>12,.2f}  (Platform ROAS: {leak_row['platform_roas']}x)")
    print(f"--------------------------------------------------------------------------")
    print(f"• Gross Order Revenue:          ${gross:>12,.2f}")
    print(f"• Customer Discounts (Coupons): -${disc:>11,.2f}  ({disc/gross:.1%} discount rate)")
    print(f"• Product Refunds (Returns):    -${ref:>11,.2f}  ({ref/(gross-disc):.1%} return rate)")
    print(f"• Net Realized Revenue:         ${gross-disc-ref:>12,.2f}")
    print(f"• Cost of Goods Sold (COGS):    -${cogs:>11,.2f}  ({cogs/(gross-disc):.1%} of sales)")
    print(f"• Carrier Shipping Costs:       -${ship:>11,.2f}")
    print(f"• Merchant Gateway Fees:        -${fees:>11,.2f}")
    print(f"--------------------------------------------------------------------------")
    print(f"• True Contribution Margin:     ${cm:>12,.2f}  (TRUE CM-ROAS: {cm/leak_row['campaign_spend']:.2f}x)")
    print("==========================================================================")


if __name__ == "__main__":
    run_verification()
