"""Synthetic HCP dataset + a real scikit-learn churn model (trained at runtime, cached)."""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

FEATURES = ["rx_trend", "calls_per_qtr", "email_engagement", "samples_used",
            "tenure_months", "competitor_share", "tickets_open", "payer_friction"]
LABELS = {
    "rx_trend": "Rx volume trend (%)", "calls_per_qtr": "Rep calls / quarter",
    "email_engagement": "Email engagement (0-100)", "samples_used": "Samples used / quarter",
    "tenure_months": "Tenure (months)", "competitor_share": "Competitor share (%)",
    "tickets_open": "Open service tickets", "payer_friction": "Payer friction (0-10)",
}


def make_dataset(n=2500, seed=42):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "rx_trend": rng.normal(0, 12, n).round(1),
        "calls_per_qtr": rng.integers(0, 12, n),
        "email_engagement": rng.integers(0, 100, n),
        "samples_used": rng.integers(0, 40, n),
        "tenure_months": rng.integers(1, 120, n),
        "competitor_share": rng.integers(0, 80, n),
        "tickets_open": rng.integers(0, 6, n),
        "payer_friction": rng.integers(0, 10, n),
    })
    # latent churn risk: declining Rx, low engagement, high competitor share & friction drive churn
    z = (-0.06 * df.rx_trend - 0.10 * df.calls_per_qtr - 0.025 * df.email_engagement
         - 0.03 * df.samples_used + 0.04 * df.competitor_share + 0.25 * df.tickets_open
         + 0.22 * df.payer_friction - 0.008 * df.tenure_months - 1.6)
    p = 1 / (1 + np.exp(-z))
    df["churned"] = (rng.random(n) < p).astype(int)
    return df


def train():
    df = make_dataset()
    X, y = df[FEATURES], df["churned"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=1, stratify=y)
    model = RandomForestClassifier(n_estimators=180, max_depth=8, random_state=1, n_jobs=-1)
    model.fit(Xtr, ytr)
    auc = roc_auc_score(yte, model.predict_proba(Xte)[:, 1])
    importances = sorted(zip(FEATURES, model.feature_importances_), key=lambda t: -t[1])
    return model, df, round(auc, 3), importances


def predict_one(model, values: dict):
    X = pd.DataFrame([[values[f] for f in FEATURES]], columns=FEATURES)
    p = float(model.predict_proba(X)[0, 1])
    tier = "🔴 High" if p > 0.6 else ("🟠 Medium" if p > 0.3 else "🟢 Low")
    if p > 0.6:
        action = "Trigger a senior-rep save play this week: address payer friction, resolve open tickets, re-establish call cadence."
    elif p > 0.3:
        action = "Proactive outreach: refresh samples, lift digital engagement, monitor Rx trend monthly."
    else:
        action = "Maintain cadence; nurture via low-cost digital channels."
    return round(p * 100, 1), tier, action


def at_risk_table(model, df, top=12):
    proba = model.predict_proba(df[FEATURES])[:, 1]
    out = df.copy()
    out.insert(0, "HCP", [f"Dr. #{i:04d}" for i in range(len(out))])
    out["Churn risk %"] = (proba * 100).round(1)
    cols = ["HCP", "Churn risk %", "rx_trend", "calls_per_qtr", "competitor_share", "payer_friction"]
    return out.sort_values("Churn risk %", ascending=False)[cols].head(top).reset_index(drop=True)
