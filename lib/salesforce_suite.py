"""Logic for the Sales Force Design & IC Suite.
Segmentation -> Targeting -> Sizing (workload build-up) -> Structure -> Incentive Comp.
Grounded in standard SFE practice (decile segmentation, workload build-up, goal-attainment payout curves).
"""
from __future__ import annotations
import numpy as np
import pandas as pd

# Demo HCP/account universe (synthetic). hcp_id mimics an NPI.
def demo_universe(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    specs = ["Endocrinology", "Cardiology", "PCP / Internal Med", "Nephrology", "Diabetology"]
    geos = ["North", "South", "East", "West", "Central"]
    pot = rng.gamma(2.2, 60, n).round(0)
    rows = []
    for i in range(n):
        rows.append({
            "hcp_id": f"1{rng.integers(100000000, 999999999)}",      # NPI-like 10-digit
            "specialty": rng.choice(specs, p=[.30, .15, .30, .10, .15]),
            "geo": rng.choice(geos),
            "potential": float(pot[i]),
            "current_volume": float(max(0, pot[i] * rng.uniform(0.1, 0.7))),
            "access": rng.choice(["High", "Medium", "Low", "No-see"], p=[.35, .35, .2, .1]),
            "competitor_share": int(rng.integers(0, 80)),
        })
    return rows


def segment(df: pd.DataFrame, a_min: int = 8, b_min: int = 5):
    """Add decile (1-10) from potential if absent, and tier A/B/C using decile cutoffs."""
    out = df.copy()
    if "decile" not in out.columns:
        try:
            out["decile"] = pd.qcut(out["potential"].rank(method="first"), 10,
                                    labels=list(range(1, 11))).astype(int)
        except Exception:
            out["decile"] = pd.cut(out["potential"], 10, labels=list(range(1, 11))).astype(int)
    out["decile"] = out["decile"].astype(int)
    out["tier"] = np.where(out["decile"] >= a_min, "A — High",
                           np.where(out["decile"] >= b_min, "B — Medium", "C — Low"))
    return out


# Default reach (% of tier to target) and frequency (calls/HCP/year)
DEFAULT_PLAN = {
    "A — High":   {"reach": 100, "freq": 12},
    "B — Medium": {"reach": 80,  "freq": 8},
    "C — Low":    {"reach": 40,  "freq": 4},
}


def target(df_seg: pd.DataFrame, plan: dict, access_aware=True):
    """Build target list + call demand per tier. Honors 'access' if present (No-see excluded)."""
    out = df_seg.copy()
    out["targeted"] = False
    out["planned_calls"] = 0
    rng = np.random.default_rng(1)
    rows = []
    for tier, p in plan.items():
        sub = out[out["tier"] == tier]
        if access_aware and "access" in out.columns:
            sub = sub[sub["access"] != "No-see"]
        # take top reach% by potential within tier
        k = int(round(len(sub) * p["reach"] / 100))
        chosen = sub.sort_values("potential", ascending=False).head(k).index
        out.loc[chosen, "targeted"] = True
        out.loc[chosen, "planned_calls"] = p["freq"]
        rows.append({"Tier": tier, "HCPs in tier": len(out[out["tier"] == tier]),
                     "Targeted": int(len(chosen)), "Freq (calls/yr)": p["freq"],
                     "Calls demanded": int(len(chosen) * p["freq"])})
    summary = pd.DataFrame(rows)
    total_calls = int(summary["Calls demanded"].sum())
    return out, summary, total_calls


def size_force(total_calls, selling_days, calls_per_day):
    capacity = max(1, selling_days * calls_per_day)
    reps = int(np.ceil(total_calls / capacity))
    return reps, capacity


def territory_balance(df_targeted: pd.DataFrame, capacity: int):
    """Calls demanded vs rep capacity by geo -> reps needed & balance flag."""
    g = (df_targeted[df_targeted["targeted"]]
         .groupby("geo")["planned_calls"].sum().reset_index(name="calls"))
    g["reps_needed"] = (g["calls"] / capacity).round(1)
    avg = g["reps_needed"].mean() if len(g) else 0
    g["balance"] = np.where(g["reps_needed"] > avg * 1.2, "Over-served",
                            np.where(g["reps_needed"] < avg * 0.8, "Under-served", "Balanced"))
    return g


def ic_curve(attainment, threshold, target_pay, accelerator, cap_pct):
    """Payout as $ for a given attainment %. Goal-attainment curve:
    <threshold -> 0; threshold..100 -> linear 0..target_pay; >100 -> accelerated, capped."""
    a = np.asarray(attainment, dtype=float)
    pay = np.zeros_like(a)
    mid = (a >= threshold) & (a <= 100)
    pay[mid] = target_pay * (a[mid] - threshold) / max(1e-9, (100 - threshold))
    hi = a > 100
    pay[hi] = target_pay * (1 + accelerator * (a[hi] - 100) / 100)
    pay = np.minimum(pay, target_pay * cap_pct / 100)
    return pay


def simulate_ic(n_reps, threshold, target_pay, accelerator, cap_pct, seed=3):
    rng = np.random.default_rng(seed)
    attain = np.clip(rng.normal(100, 16, n_reps), 50, 175)
    pay = ic_curve(attain, threshold, target_pay, accelerator, cap_pct)
    budget = n_reps * target_pay
    return {
        "attain": attain, "pay": pay,
        "total_payout": float(pay.sum()),
        "budget": float(budget),
        "vs_budget": round((pay.sum() / budget - 1) * 100, 1) if budget else 0,
        "avg_payout_pct": round(pay.mean() / target_pay * 100, 1) if target_pay else 0,
        "pct_above_target": round((attain > 100).mean() * 100, 1),
        "pct_unpaid": round((attain < threshold).mean() * 100, 1),
    }
