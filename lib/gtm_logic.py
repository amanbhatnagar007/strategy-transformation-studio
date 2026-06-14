"""GTM decision logic: route-to-market scoring + 5-year business case."""
from __future__ import annotations

def score_routes(asp, complexity, digital, fragmentation, presence, model, volume_units):
    """Return ranked list of (route, score 0-100, rationale)."""
    high_asp = min(100, asp / 5000 * 100)        # $5k+ → high
    s = {
        "Direct sales force":
            0.40 * high_asp + 0.30 * complexity * 10 + 0.20 * presence * 10 + 0.10 * (100 - fragmentation * 10),
        "Distributor / indirect":
            0.35 * fragmentation * 10 + 0.30 * (100 - high_asp) + 0.20 * (100 - presence * 10) + 0.15 * min(100, volume_units / 200),
        "Hybrid (direct + channel)":
            0.30 * high_asp + 0.25 * fragmentation * 10 + 0.25 * complexity * 10 + 0.20 * 60,
        "Digital / e-commerce":
            0.45 * digital * 10 + 0.30 * (100 - high_asp) + 0.25 * min(100, volume_units / 150),
        "Strategic partnership / OEM":
            0.40 * (100 - presence * 10) + 0.30 * complexity * 10 + 0.30 * 50,
    }
    if model in ("Subscription", "Pay-per-use"):
        s["Direct sales force"] += 8
        s["Digital / e-commerce"] += 10
    ranked = sorted(((k, round(min(99, v))) for k, v in s.items()), key=lambda x: -x[1])
    rationale = {
        "Direct sales force": "high ASP & clinical complexity reward owned relationships",
        "Distributor / indirect": "fragmented buyers and reach favor channel leverage",
        "Hybrid (direct + channel)": "direct in core accounts, channel for the long tail",
        "Digital / e-commerce": "digital-mature, transactional buying behavior",
        "Strategic partnership / OEM": "limited local presence — partner to enter fast",
    }
    return [(k, v, rationale[k]) for k, v in ranked]


def prioritize_markets(markets):
    """Tier markets by attractiveness + ease. Returns list of dicts with tier & sequence."""
    scored = []
    for name, region, attract, ease, growth in markets:
        composite = round(0.6 * attract + 0.4 * ease)
        scored.append({"country": name, "region": region, "attract": attract,
                       "ease": ease, "growth": growth, "composite": composite})
    scored.sort(key=lambda d: -d["composite"])
    for i, d in enumerate(scored):
        d["tier"] = "Tier 1 — Now" if i < 3 else ("Tier 2 — Next" if i < 6 else "Tier 3 — Later")
        d["wave"] = "Wave 1 (0–12m)" if i < 3 else ("Wave 2 (12–24m)" if i < 6 else "Wave 3 (24m+)")
    return scored


def business_case(invest_m, asp, units_y1, vol_cagr, gross_margin, channel,
                  discount=0.12, years=5):
    """5-year P&L + cash flow for the chosen channel.
    Direct: higher fixed opex, full margin. Indirect: distributor margin haircut, lower opex.
    """
    distributor_take = {"Direct sales force": 0.0, "Distributor / indirect": 0.30,
                        "Hybrid (direct + channel)": 0.15, "Digital / e-commerce": 0.05,
                        "Strategic partnership / OEM": 0.20}.get(channel, 0.15)
    # opex as % of revenue (direct carries more commercial fixed cost)
    opex_pct = {"Direct sales force": 0.34, "Distributor / indirect": 0.16,
                "Hybrid (direct + channel)": 0.26, "Digital / e-commerce": 0.20,
                "Strategic partnership / OEM": 0.18}.get(channel, 0.25)

    rows, cum, npv = [], -invest_m, -invest_m
    for y in range(1, years + 1):
        units = units_y1 * ((1 + vol_cagr / 100) ** (y - 1))
        gross_rev = units * asp / 1_000_000                      # $M
        net_rev = gross_rev * (1 - distributor_take)
        gp = net_rev * gross_margin / 100
        opex = net_rev * opex_pct
        ebitda = gp - opex
        cum += ebitda
        npv += ebitda / ((1 + discount) ** y)
        rows.append({"Year": f"Y{y}", "Units": round(units), "Net revenue ($M)": round(net_rev, 1),
                     "Gross profit ($M)": round(gp, 1), "EBITDA ($M)": round(ebitda, 1),
                     "Cumulative cash ($M)": round(cum, 1)})
    # payback year
    payback = next((r["Year"] for r in rows if r["Cumulative cash ($M)"] >= 0), ">5y")
    total_ebitda = sum(r["EBITDA ($M)"] for r in rows)
    roi = round((total_ebitda - invest_m) / invest_m * 100) if invest_m else 0
    return {"rows": rows, "npv": round(npv, 1), "payback": payback, "roi": roi,
            "distributor_take": int(distributor_take * 100), "opex_pct": int(opex_pct * 100),
            "peak_ebitda": round(rows[-1]["EBITDA ($M)"], 1)}


def exec_summary(product, sector, top_route, top_markets, bc):
    """Deterministic narrative — board-ready, no API key."""
    m = ", ".join(top_markets[:3])
    verdict = "attractive" if bc["roi"] > 60 else ("viable" if bc["roi"] > 0 else "challenged")
    return (
        f"For **{product}** in {sector}, the recommended route-to-market is **{top_route}**. "
        f"Prioritize **{m}** in Wave 1 — the highest composite of market attractiveness and ease of entry. "
        f"The business case is **{verdict}**: ~{bc['roi']}% 5-year ROI, NPV of ${bc['npv']}M (12% discount), "
        f"payback in {bc['payback']}, reaching ${bc['peak_ebitda']}M EBITDA by Year 5. "
        f"Sequence investment behind Wave-1 markets, validate the channel economics "
        f"(distributor take {bc['distributor_take']}%, commercial opex {bc['opex_pct']}% of revenue), "
        f"then scale to Tier-2 markets as the model proves out."
    )
