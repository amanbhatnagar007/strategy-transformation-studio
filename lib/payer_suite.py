"""Logic for the Payer & Reimbursement Suite.
Contract profitability (CPT-level, identifier-keyed) · Medicare Advantage value upside.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def demo_contracts(n=60, seed=5):
    rng = np.random.default_rng(seed)
    payers = ["Aetna", "UnitedHealth", "Cigna", "BCBS", "Humana", "Medicare", "Medicaid"]
    cpts = ["99213", "99214", "99203", "93000", "80053", "70450", "99232", "45378"]
    rows = []
    for _ in range(n):
        cost = rng.uniform(40, 220)
        rate = cost * rng.uniform(0.8, 1.8)          # some below cost (loss-makers)
        rows.append({
            "contract_id": f"{rng.choice(payers)}-{rng.choice(cpts)}",
            "payer": rng.choice(payers),
            "service": rng.choice(cpts),
            "encounters": int(rng.integers(50, 4000)),
            "contracted_rate": round(rate, 2),
            "cost_per_unit": round(cost, 2),
            "denial_rate": round(rng.uniform(0, 18), 1),
        })
    return rows


def analyze_contracts(df: pd.DataFrame):
    out = df.copy()
    out["margin_per"] = out["contracted_rate"] - out["cost_per_unit"]
    out["total_margin"] = out["margin_per"] * out["encounters"]
    out["margin_pct"] = np.where(out["contracted_rate"] != 0,
                                 out["margin_per"] / out["contracted_rate"] * 100, 0).round(1)
    out = out.sort_values("total_margin")
    return out


def margin_tier(margin_pct):
    return "🔴 Loss-making" if margin_pct < 0 else ("🟠 Thin" if margin_pct < 15 else "🟢 Healthy")


def medicare_value(members, base_pmpm, raf_current, raf_target, care_pmpm, mlr_improve_pp):
    """Estimate MA revenue & margin upside from better risk capture + care mgmt + MLR."""
    months = 12
    rev_current = members * base_pmpm * raf_current * months
    rev_target = members * base_pmpm * raf_target * months
    risk_uplift = rev_target - rev_current
    care_cost = members * care_pmpm * months
    mlr_savings = rev_target * (mlr_improve_pp / 100)
    margin_upside = risk_uplift + mlr_savings - care_cost
    return {
        "rev_current": rev_current, "rev_target": rev_target,
        "risk_uplift": risk_uplift, "care_cost": care_cost, "mlr_savings": mlr_savings,
        "margin_upside": margin_upside,
        "per_member": margin_upside / members if members else 0,
    }
