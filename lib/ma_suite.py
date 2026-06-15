"""Shared logic for the M&A suites: target screening, Day-1 readiness, carve-out, separation org."""
from __future__ import annotations
import numpy as np
import pandas as pd

# ---------- Target screening ----------
TARGET_CRITERIA = {
    "strategic_fit": "Strategic fit", "financial": "Financial health", "synergy": "Synergy potential",
    "risk": "Cultural / integration risk", "market": "Market position",
}


def demo_targets():
    return [
        {"target": "Alpha Diagnostics", "strategic_fit": 88, "financial": 72, "synergy": 80, "risk": 30, "market": 75},
        {"target": "Beta Therapeutics", "strategic_fit": 70, "financial": 85, "synergy": 60, "risk": 45, "market": 82},
        {"target": "Gamma Devices", "strategic_fit": 92, "financial": 55, "synergy": 88, "risk": 60, "market": 50},
        {"target": "Delta Health IT", "strategic_fit": 65, "financial": 78, "synergy": 72, "risk": 25, "market": 68},
        {"target": "Epsilon Care", "strategic_fit": 80, "financial": 60, "synergy": 55, "risk": 70, "market": 45},
        {"target": "Zeta Pharma Svcs", "strategic_fit": 58, "financial": 90, "synergy": 65, "risk": 35, "market": 88},
    ]


def score_targets(df, weights):
    d = df.copy()
    for c in TARGET_CRITERIA:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce").clip(0, 100)
    d["Weighted score"] = (
        d["strategic_fit"] * weights["strategic_fit"] + d["financial"] * weights["financial"]
        + d["synergy"] * weights["synergy"] + (100 - d["risk"]) * weights["risk"]
        + d["market"] * weights["market"]).round(1)
    d = d.sort_values("Weighted score", ascending=False).reset_index(drop=True)
    d.insert(0, "Rank", range(1, len(d) + 1))
    return d


# ---------- Day-1 readiness ----------
WORKSTREAMS = {"Sales": 6, "Marketing": 4, "Customer service": 4, "Pricing / contracts": 7,
               "IT / CRM": 7, "Supply": 6, "People / org": 5, "Legal / compliance": 6}
WS_DEFAULTS = {"Sales": 75, "Marketing": 60, "Customer service": 55, "Pricing / contracts": 45,
               "IT / CRM": 40, "Supply": 70, "People / org": 80, "Legal / compliance": 65}


def rag(pct):
    return "🔴 Red" if pct < 50 else ("🟠 Amber" if pct < 80 else "🟢 Green")


def day1_readiness(completion, target_days):
    wsum = sum(WORKSTREAMS.values())
    rows = [{"Workstream": ws, "Completion %": completion[ws], "Weight %": round(w / wsum * 100, 1),
             "RAG": rag(completion[ws])} for ws, w in WORKSTREAMS.items()]
    df = pd.DataFrame(rows)
    overall = round(sum(completion[ws] * w for ws, w in WORKSTREAMS.items()) / wsum, 1)
    n_red = int((df["RAG"] == "🔴 Red").sum())
    days_to_ready = round(target_days * ((100 - overall) / 100) * (1 + 0.25 * n_red))
    confidence = ("High" if overall >= 80 and n_red == 0 else
                  "Moderate" if overall >= 65 and n_red <= 1 else "Low")
    return df, overall, n_red, days_to_ready, confidence


# ---------- Carve-out ----------
TSA_FUNCTIONS = {"IT / applications": 1.4, "Finance / ERP": 1.2, "HR / payroll": 0.8,
                 "Procurement": 0.9, "Facilities": 0.7}


def carveout(tgt_rev, shared_pct, entanglement, n_tsa, tsa_months):
    shared_cost = tgt_rev * shared_pct / 100
    stranded_frac = min(0.6, 0.18 + 0.04 * entanglement)
    stranded_cost = round(shared_cost * stranded_frac, 1)
    separation_cost = round(shared_cost * (0.35 + 0.05 * entanglement) + n_tsa * 0.4, 1)
    months_to_standalone = round(tsa_months + entanglement * 0.6 + n_tsa * 0.15)
    complexity = ("Low" if entanglement <= 3 and n_tsa <= 6 else
                  "Moderate" if entanglement <= 6 and n_tsa <= 18 else "High")
    fsum = sum(TSA_FUNCTIONS.values())
    rows = []
    for fn, factor in TSA_FUNCTIONS.items():
        exit_m = round(min(tsa_months * factor / (fsum / len(TSA_FUNCTIONS)), tsa_months + entanglement))
        cnt = max(1, round(n_tsa * factor / fsum)) if n_tsa else 0
        rows.append({"Function": fn, "TSAs": cnt, "Exit month": exit_m})
    return {"shared_cost": round(shared_cost, 1), "stranded_cost": stranded_cost,
            "stranded_pct": round(stranded_cost / tgt_rev * 100, 1) if tgt_rev else 0,
            "separation_cost": separation_cost, "months_to_standalone": months_to_standalone,
            "complexity": complexity, "tsa_df": pd.DataFrame(rows)}


def separation_org_dot(tsa_df):
    """Two-entity separation org with TSA dependencies (RemainCo provides services to DivestCo)."""
    lines = ['digraph G {', 'graph [bgcolor="transparent", rankdir=LR, nodesep=0.25, ranksep=0.8];',
             'node [shape=box, style=filled, fontcolor="#EAF0FF", color="#8B6CFF", fillcolor="#1b2138", '
             'fontname="Helvetica", fontsize=11];', 'edge [color="#5b6488"];']
    lines.append('Parent [label="Parent Co\\n(pre-separation)", fillcolor="#23314f", color="#22D3EE"];')
    lines.append('Remain [label="RemainCo", fillcolor="#143042", color="#22D3EE"];')
    lines.append('Divest [label="DivestCo\\n(standalone target)", fillcolor="#3a2350", color="#EC4899"];')
    lines.append('Parent -> Remain; Parent -> Divest;')
    for i, r in tsa_df.reset_index(drop=True).iterrows():
        fn = r["Function"]
        rn = f"r{i}"
        lines.append(f'{rn} [label="{fn}\\n(TSA → {r["Exit month"]} mo)", fontsize=10];')
        lines.append(f'Remain -> {rn};')
        lines.append(f'{rn} -> Divest [style=dashed, color="#EC4899", label="TSA"];')
    lines.append('}')
    return "\n".join(lines)


# ---------- Deal value tracking ----------
CURVES = {"Linear": [0.25, 0.50, 0.75, 1.00, 1, 1, 1, 1],
          "S-curve (back-loaded)": [0.12, 0.32, 0.65, 1.00, 1, 1, 1, 1],
          "Front-loaded": [0.40, 0.70, 0.90, 1.00, 1, 1, 1, 1]}


def planned_increments(target, curve, n):
    frac = CURVES[curve][:n]
    frac = [f / frac[-1] for f in frac]
    cum = [round(target * f, 1) for f in frac]
    return [round(cum[0], 1)] + [round(cum[i] - cum[i - 1], 1) for i in range(1, n)]


def track(df, target):
    d = df.copy().reset_index(drop=True)
    d["Planned cum"] = d["planned"].cumsum().round(1)
    d["Actual cum"] = d["actual"].cumsum().round(1)
    d["Variance ($M)"] = (d["Actual cum"] - d["Planned cum"]).round(1)
    captured = d["Actual cum"].iloc[-1]
    pct = round(captured / target * 100, 1) if target else 0
    ratio = (captured / d["Planned cum"].iloc[-1]) if d["Planned cum"].iloc[-1] else 0
    projected = round(d["planned"].sum() * ratio, 1)
    return d, pct, projected
