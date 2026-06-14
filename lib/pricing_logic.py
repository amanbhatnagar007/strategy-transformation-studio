"""Pricing corridor & market-entry mode heuristics."""
from __future__ import annotations
import numpy as np


def price_corridor(unit_cost, target_margin, competitor_price, value_to_customer):
    """Floor (cost-plus), ceiling (value-based), reference (competitor), recommended."""
    floor = unit_cost / (1 - target_margin / 100.0) if target_margin < 100 else unit_cost * 2
    ceiling = max(value_to_customer, floor * 1.01)
    reference = competitor_price
    # recommended: anchor near competitor but inside [floor, ceiling], nudged toward value
    rec = 0.55 * reference + 0.45 * ((floor + ceiling) / 2)
    rec = float(np.clip(rec, floor, ceiling))
    return {
        "floor": round(floor, 2),
        "ceiling": round(ceiling, 2),
        "reference": round(reference, 2),
        "recommended": round(rec, 2),
    }


def demand_curve(corr, unit_cost, competitor_price, elasticity, base_volume):
    """Constant-elasticity demand vs competitor reference. Returns prices, volumes, revenue, profit."""
    prices = np.linspace(corr["floor"], corr["ceiling"], 40)
    # volume = base * (price/ref)^elasticity ; elasticity negative
    ref = max(competitor_price, 0.01)
    vols = base_volume * (prices / ref) ** elasticity
    revenue = prices * vols
    profit = (prices - unit_cost) * vols
    return prices, vols, revenue, profit


def estimate_at(price, unit_cost, competitor_price, elasticity, base_volume):
    ref = max(competitor_price, 0.01)
    vol = base_volume * (price / ref) ** elasticity
    rev = price * vol
    profit = (price - unit_cost) * vol
    margin = (price - unit_cost) / price * 100 if price else 0
    return {"volume": vol, "revenue": rev, "profit": profit, "margin": round(margin, 1)}


def entry_mode(presence, margin, value_to_customer, competitor_price):
    """Recommend entry mode from local presence (0-10) and economics."""
    premium = value_to_customer > competitor_price * 1.15
    if presence >= 7:
        mode = "Organic / direct"
        why = "strong local presence supports owning the customer relationship and capturing full margin"
    elif presence >= 4:
        mode = "Partner / distributor" if margin > 35 else "Distributor"
        why = "moderate presence — leverage a local channel for reach while you build infrastructure"
    elif presence >= 2:
        mode = "Distributor"
        why = "limited footprint favors a distributor to access the market with minimal fixed cost"
    else:
        mode = "M&A / acquire local player" if premium and margin > 40 else "Partner / licensing"
        why = ("near-zero presence and strong economics justify acquiring a local platform"
               if premium and margin > 40
               else "near-zero presence — enter via partnership/licensing to de-risk")
    return mode, why


def pricing_summary(corr, est, mode, why, target_margin):
    pos = ("at a premium to" if corr["recommended"] > corr["reference"] * 1.03
           else ("at a discount to" if corr["recommended"] < corr["reference"] * 0.97
                 else "in line with"))
    return (
        f"The viable price corridor runs from a **${corr['floor']:,.2f}** cost-plus floor (to protect "
        f"{target_margin}% margin) to a **${corr['ceiling']:,.2f}** value ceiling, with competitors "
        f"referencing **${corr['reference']:,.2f}**. The recommended launch price of "
        f"**${corr['recommended']:,.2f}** sits {pos} the competitor — yielding an estimated "
        f"**${est['revenue']:,.0f}** revenue at a **{est['margin']}%** unit margin given the assumed "
        f"elasticity. For market entry, lead with **{mode}**: {why}. Validate value-to-customer and "
        f"elasticity with primary research before committing — both swing the recommended price materially."
    )
