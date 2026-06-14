"""M&A synergy estimation: cost + revenue synergies, phasing, valuation impact."""

def estimate_synergies(acq_rev, tgt_rev, tgt_sga_pct, tgt_cogs_pct, overlap,
                       cross_sell, pricing_power, deal_value, integration_cost,
                       discount=0.10, years=3):
    """All $ in $M. overlap/cross_sell/pricing_power are 0-1 sliders."""
    tgt_sga = tgt_rev * tgt_sga_pct / 100
    tgt_cogs = tgt_rev * tgt_cogs_pct / 100

    # Cost synergies
    sga_syn = tgt_sga * overlap * 0.45            # remove duplicate corporate/commercial SG&A
    proc_syn = tgt_cogs * 0.04 * (0.5 + overlap)  # procurement / scale on COGS
    footprint_syn = tgt_sga * 0.10 * overlap      # facilities / footprint
    cost_syn = sga_syn + proc_syn + footprint_syn

    # Revenue synergies (run-rate EBITDA contribution, conservative margin)
    cross_rev = min(acq_rev, tgt_rev) * cross_sell * 0.06
    price_rev = (acq_rev + tgt_rev) * pricing_power * 0.015
    rev_syn_margin = 0.35
    rev_syn = (cross_rev + price_rev) * rev_syn_margin

    total_runrate = cost_syn + rev_syn

    # Phasing to run-rate (% realized each year)
    phase = [0.40, 0.75, 1.00][:years]
    rows, npv = [], -integration_cost
    for y, f in enumerate(phase, 1):
        realized = total_runrate * f
        rows.append({"Year": f"Y{y}", "Cost syn ($M)": round(cost_syn * f, 1),
                     "Revenue syn ($M)": round(rev_syn * f, 1),
                     "Total realized ($M)": round(realized, 1)})
        npv += realized / ((1 + discount) ** y)

    pct_of_deal = round(total_runrate / deal_value * 100, 1) if deal_value else 0
    return {
        "cost_breakdown": {"SG&A overlap": round(sga_syn, 1), "Procurement / COGS": round(proc_syn, 1),
                           "Footprint": round(footprint_syn, 1)},
        "rev_breakdown": {"Cross-sell": round(cross_rev * rev_syn_margin, 1),
                          "Pricing power": round(price_rev * rev_syn_margin, 1)},
        "cost_syn": round(cost_syn, 1), "rev_syn": round(rev_syn, 1),
        "total_runrate": round(total_runrate, 1), "rows": rows,
        "npv": round(npv, 1), "pct_of_deal": pct_of_deal,
        "integration_cost": integration_cost,
        "payback_ratio": round(integration_cost / total_runrate, 1) if total_runrate else 0,
    }


def synergy_summary(s, deal_value):
    verdict = ("highly value-accretive" if s["pct_of_deal"] > 8 else
               "value-accretive" if s["pct_of_deal"] > 4 else "modest")
    return (
        f"Estimated run-rate synergies of **${s['total_runrate']}M** "
        f"(~{s['pct_of_deal']}% of the ${deal_value}M deal value) — split **${s['cost_syn']}M cost** and "
        f"**${s['rev_syn']}M revenue** synergies. At a 10% discount the synergy NPV is **${s['npv']}M** net of "
        f"${s['integration_cost']}M integration cost, implying a **{verdict}** transaction. "
        f"Cost synergies (SG&A de-duplication, procurement scale, footprint) are higher-confidence and front-loaded; "
        f"revenue synergies (cross-sell, pricing) carry execution risk and should be diligence-validated before "
        f"they are credited to the deal model."
    )
