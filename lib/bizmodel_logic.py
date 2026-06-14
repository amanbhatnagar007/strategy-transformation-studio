"""Commercial business-model comparison: capital vs subscription vs pay-per-use vs hybrid."""
from __future__ import annotations

MODELS = ["Capital / one-time", "Subscription", "Pay-per-use", "Hybrid"]


def simulate(new_customers_y1, growth, capital_price, sub_price_yr, ppu_price_yr,
             hybrid_upfront, hybrid_price_yr, retention, gross_margin, years=5):
    """Return per-model 5-yr economics.

    - Capital: revenue is one-time at acquisition (no recurring); customers don't compound.
    - Subscription / Pay-per-use: recurring; installed base retained at `retention`.
    - Hybrid: smaller upfront + a recurring fee.
    """
    ret = retention / 100.0
    gm = gross_margin / 100.0

    def new_custs(y):
        return new_customers_y1 * ((1 + growth / 100.0) ** (y - 1))

    out = {}

    # installed base helper for recurring models
    def recurring(price_yr, upfront=0.0):
        rows, base, cum = [], 0.0, 0.0
        for y in range(1, years + 1):
            adds = new_custs(y)
            base = base * ret + adds
            rev = base * price_yr + adds * upfront
            cum += rev
            rows.append({"Year": f"Y{y}", "Active customers": round(base),
                         "Revenue ($)": round(rev), "Cumulative ($)": round(cum)})
        # LTV: avg annual recurring revenue * margin * customer lifetime (1/churn)
        churn = max(0.01, 1 - ret)
        ltv = (price_yr * gm) / churn + upfront * gm
        return rows, cum, ltv

    # capital / one-time
    rows, cum = [], 0.0
    for y in range(1, years + 1):
        adds = new_custs(y)
        rev = adds * capital_price
        cum += rev
        rows.append({"Year": f"Y{y}", "Active customers": round(adds),
                     "Revenue ($)": round(rev), "Cumulative ($)": round(cum)})
    cap_ltv = capital_price * gm  # one purchase
    out["Capital / one-time"] = {"rows": rows, "cum_rev": cum, "ltv": cap_ltv,
                                 "recurring": False}

    sub_rows, sub_cum, sub_ltv = recurring(sub_price_yr)
    out["Subscription"] = {"rows": sub_rows, "cum_rev": sub_cum, "ltv": sub_ltv, "recurring": True}

    ppu_rows, ppu_cum, ppu_ltv = recurring(ppu_price_yr)
    out["Pay-per-use"] = {"rows": ppu_rows, "cum_rev": ppu_cum, "ltv": ppu_ltv, "recurring": True}

    hyb_rows, hyb_cum, hyb_ltv = recurring(hybrid_price_yr, upfront=hybrid_upfront)
    out["Hybrid"] = {"rows": hyb_rows, "cum_rev": hyb_cum, "ltv": hyb_ltv, "recurring": True}

    # payback per customer: acquisition proxy = first-year price; payback = years to recover via margin
    return out


def recommend(out, gross_margin):
    """Pick a model balancing 5-yr cumulative revenue and LTV durability."""
    gm = gross_margin / 100.0
    scored = []
    for m, d in out.items():
        # weight cumulative revenue and LTV; reward recurring durability
        durability = 1.15 if d["recurring"] else 1.0
        score = (d["cum_rev"] * 0.6 + d["ltv"] * 50 * 0.4) * durability
        scored.append((m, score, d))
    scored.sort(key=lambda x: -x[1])
    return scored[0][0], scored


def bm_summary(out, rec, gross_margin, years=5):
    d = out[rec]
    others = sorted(((m, v["cum_rev"]) for m, v in out.items()), key=lambda x: -x[1])
    runner = next((m for m, _ in others if m != rec), rec)
    nature = "recurring, retention-driven" if d["recurring"] else "transactional, one-time"
    return (
        f"Across a {years}-year horizon, **{rec}** is the recommended commercial model: it delivers the "
        f"strongest blend of cumulative revenue (~${d['cum_rev']:,.0f}) and customer lifetime value "
        f"(~${d['ltv']:,.0f} at {gross_margin}% gross margin). Its economics are {nature}, which "
        f"{'compounds an installed base and smooths revenue' if d['recurring'] else 'front-loads cash but must be re-won each cycle'}. "
        f"**{runner}** is the closest alternative. Pressure-test retention and price assumptions before "
        f"committing — a recurring model only wins if churn stays low and the installed base actually compounds."
    )
