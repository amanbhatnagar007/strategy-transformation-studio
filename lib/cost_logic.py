"""Cost takeout / org-redesign model: savings by lever, org structure, phasing."""

def org_shape(headcount, layers, target_span):
    """Estimate managers vs ICs from layers & span; flag delayering opportunity."""
    # geometric org: top down, each layer multiplies by span
    current_span = headcount ** (1 / max(layers, 1))
    excess_layers = max(0, layers - 6)
    span_gap = max(0, target_span - current_span)
    # managers ≈ headcount / span
    managers = round(headcount / max(current_span, 1.5))
    return {"current_span": round(current_span, 1), "managers": managers,
            "excess_layers": excess_layers, "span_gap": round(span_gap, 1)}


def cost_savings(cost_base, headcount, avg_cost, layers, target_span,
                 procurement_addr, automation_ready, footprint_cost):
    """All $ in $M except avg_cost ($/FTE in $k). Returns levers + phasing."""
    org = org_shape(headcount, layers, target_span)

    # Lever 1: de-layering / spans (reduce managers toward target span)
    target_managers = round(headcount / max(target_span, 1.5))
    mgr_reduction = max(0, org["managers"] - target_managers)
    # ~55% realization — not every delayered role converts to cash; some redeploy
    org_save = mgr_reduction * (avg_cost * 1.4) / 1000 * 0.55  # $M

    # Lever 2: automation / process (share of addressable opex)
    auto_save = cost_base * 0.12 * automation_ready

    # Lever 3: procurement / third-party spend
    proc_save = procurement_addr * 0.08

    # Lever 4: footprint / facilities
    foot_save = footprint_cost * 0.25

    levers = {"Org de-layering & spans": round(org_save, 1),
              "Automation & process": round(auto_save, 1),
              "Procurement / vendor": round(proc_save, 1),
              "Footprint / facilities": round(foot_save, 1)}
    total = round(sum(levers.values()), 1)
    pct = round(total / cost_base * 100, 1) if cost_base else 0

    # Phasing over 3 years (quick wins first)
    phase = [0.45, 0.80, 1.0]
    rows = [{"Year": f"Y{y}", "Run-rate savings ($M)": round(total * f, 1),
             "% of target": f"{int(f*100)}%"} for y, f in enumerate(phase, 1)]

    return {"org": org, "levers": levers, "total": total, "pct": pct,
            "mgr_reduction": mgr_reduction, "target_managers": target_managers, "rows": rows}


def cost_summary(c, cost_base, ebitda_pct=15):
    ebitda_uplift = round(c["total"], 1)
    return (
        f"Identified **${c['total']}M** in addressable cost takeout (~{c['pct']}% of the ${cost_base}M base) "
        f"across four levers. The largest, highest-confidence pool is structural: spans currently average "
        f"**{c['org']['current_span']}** with **{c['org']['excess_layers']} excess layers**, so moving to the "
        f"target span removes ~**{c['mgr_reduction']} management roles**. Sequence the quick wins "
        f"(procurement, spans) in Year 1 to self-fund the transformation, then pursue automation and footprint "
        f"in Years 2–3. At full run-rate this flows roughly 1:1 to EBITDA — a material margin improvement "
        f"that can be reinvested in growth."
    )
