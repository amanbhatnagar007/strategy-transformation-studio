"""Logic for the HCP Engagement & Churn Suite.
Churn/retention (NPI-keyed ML) · action plan by risk tier · omni-channel mix.
Reuses the RandomForest from lib/churn_model.py and scores an uploaded panel by NPI.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from lib.churn_model import make_dataset, train, FEATURES, LABELS


def feature_medians():
    df = make_dataset()
    return {f: float(df[f].median()) for f in FEATURES}


def demo_panel(n=400, seed=11):
    """Prescriber panel with an NPI-like id + behavioral features."""
    base = make_dataset(n=n, seed=seed).drop(columns=["churned"])
    rng = np.random.default_rng(seed)
    specs = ["Endocrinology", "Cardiology", "PCP / Internal Med", "Nephrology", "Diabetology"]
    base.insert(0, "hcp_id", [f"1{rng.integers(100000000, 999999999)}" for _ in range(len(base))])
    base.insert(1, "specialty", rng.choice(specs, len(base)))
    base.insert(2, "geo", rng.choice(["North", "South", "East", "West", "Central"], len(base)))
    base["current_volume"] = (rng.gamma(2, 40, len(base))).round(0)
    return base.to_dict("records")


def score_panel(model, df: pd.DataFrame):
    """Score an uploaded/demo panel by NPI. Missing optional features filled with training medians."""
    med = feature_medians()
    X = pd.DataFrame(index=df.index)
    used, imputed = [], []
    for f in FEATURES:
        if f in df.columns:
            X[f] = pd.to_numeric(df[f], errors="coerce").fillna(med[f]); used.append(f)
        else:
            X[f] = med[f]; imputed.append(f)
    proba = model.predict_proba(X)[:, 1]
    out = df.copy()
    out["churn_risk"] = (proba * 100).round(1)
    return out, used, imputed


def risk_tier(pct, hi=60, mid=30):
    return "🔴 High" if pct >= hi else ("🟠 Medium" if pct >= mid else "🟢 Low")


# ---------- Omni-channel optimization ----------
DEFAULT_CHANNELS = {
    "Field call":      {"cost": 180, "coef": 0.85},
    "Inside sales":    {"cost": 45,  "coef": 0.55},
    "Email":           {"cost": 3,   "coef": 0.30},
    "Webinar":         {"cost": 25,  "coef": 0.45},
    "Web / portal":    {"cost": 8,   "coef": 0.35},
}


def channel_response(spend, cost, coef, saturation=120000):
    """Saturating response: conversions from spend on a channel."""
    touches = spend / max(cost, 1)
    return coef * saturation * (1 - np.exp(-touches / (saturation / 3)))


def optimize_mix(total_budget, channels, steps=40):
    """Greedy marginal-return allocation across channels."""
    alloc = {c: 0.0 for c in channels}
    step = total_budget / steps
    for _ in range(steps):
        best, best_gain = None, -1
        for c, p in channels.items():
            cur = channel_response(alloc[c], p["cost"], p["coef"])
            nxt = channel_response(alloc[c] + step, p["cost"], p["coef"])
            if nxt - cur > best_gain:
                best_gain, best = nxt - cur, c
        alloc[best] += step
    conv = {c: channel_response(alloc[c], channels[c]["cost"], channels[c]["coef"]) for c in channels}
    return alloc, conv
