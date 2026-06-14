"""Sales force sizing & territory design heuristics."""
from __future__ import annotations


def capacity_per_rep(selling_days: int, calls_per_day: float) -> float:
    """Annual call capacity of a single rep."""
    return selling_days * calls_per_day


def size_segments(segments, selling_days, calls_per_day, current_reps):
    """segments: list of dicts {tier, accounts, calls_per_account}.
    Returns sizing dict with per-segment demand and totals.
    """
    cap = capacity_per_rep(selling_days, calls_per_day)
    rows, total_calls = [], 0.0
    for s in segments:
        demand = s["accounts"] * s["calls_per_account"]
        total_calls += demand
        rows.append({
            "Segment": s["tier"],
            "Accounts": int(s["accounts"]),
            "Calls / account / yr": round(s["calls_per_account"], 1),
            "Annual calls": round(demand),
        })
    reps_required = total_calls / cap if cap else 0
    reps_required_ceil = int(-(-reps_required // 1))  # ceil
    coverage = min(100.0, current_reps / reps_required * 100) if reps_required else 100.0
    gap = reps_required_ceil - current_reps
    # workload balance: calls per rep if current reps spread evenly
    workload = total_calls / current_reps if current_reps else float("inf")
    return {
        "rows": rows,
        "capacity": cap,
        "total_calls": total_calls,
        "reps_required": reps_required,
        "reps_required_ceil": reps_required_ceil,
        "coverage": round(coverage, 1),
        "gap": gap,
        "workload_per_current_rep": workload,
        "current_reps": current_reps,
    }


def size_from_df(df, selling_days, calls_per_day, current_reps):
    """df columns: account, segment, annual_potential, calls_needed."""
    cap = capacity_per_rep(selling_days, calls_per_day)
    grp = df.groupby("segment", dropna=False).agg(
        accounts=("account", "count"),
        annual_calls=("calls_needed", "sum"),
        potential=("annual_potential", "sum"),
    ).reset_index()
    rows, total_calls = [], 0.0
    for _, r in grp.iterrows():
        total_calls += r["annual_calls"]
        rows.append({
            "Segment": str(r["segment"]),
            "Accounts": int(r["accounts"]),
            "Annual calls": round(r["annual_calls"]),
            "Potential ($)": round(r["potential"]),
        })
    reps_required = total_calls / cap if cap else 0
    reps_required_ceil = int(-(-reps_required // 1))
    coverage = min(100.0, current_reps / reps_required * 100) if reps_required else 100.0
    return {
        "rows": rows,
        "capacity": cap,
        "total_calls": total_calls,
        "reps_required": reps_required,
        "reps_required_ceil": reps_required_ceil,
        "coverage": round(coverage, 1),
        "gap": reps_required_ceil - current_reps,
        "current_reps": current_reps,
    }


def sf_summary(z):
    gap = z["gap"]
    if gap > 0:
        verdict = (f"under-resourced — the territory demands ~{z['reps_required_ceil']} reps but only "
                   f"{z['current_reps']} are deployed, a gap of {gap}")
        action = ("hire/redeploy to close the gap, or de-prioritize the lowest-value tier so the "
                  "remaining reps cover high-potential accounts at target frequency")
    elif gap < 0:
        verdict = (f"over-resourced — {z['current_reps']} reps exceed the ~{z['reps_required_ceil']} "
                   f"the call plan requires by {abs(gap)}")
        action = ("reallocate capacity to white-space accounts, raise call frequency on top tiers, "
                  "or capture the cost saving")
    else:
        verdict = f"well-matched — {z['current_reps']} reps align to the ~{z['reps_required_ceil']} required"
        action = "hold structure and monitor account migration between tiers"
    return (
        f"The call plan generates **{z['total_calls']:,.0f} annual calls**, and at "
        f"**{z['capacity']:,.0f} calls per rep per year** the field force is **{verdict}**. "
        f"Coverage stands at **{z['coverage']}%**. Recommendation: {action}. "
        f"Validate calls-per-account targets against account potential before locking headcount — "
        f"over-calling low-tier accounts is the most common source of wasted field cost."
    )
