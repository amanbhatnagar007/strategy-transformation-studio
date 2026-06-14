"""Incentive compensation plan design: payout curve + rep-population cost simulation."""
from __future__ import annotations
import numpy as np


def payout_for_attainment(att_pct, target_total, base_pct, threshold,
                          accelerator, cap):
    """Return total earnings ($) for a given % quota attainment.

    - base is guaranteed; variable (target_total - base) is at-risk and tied to attainment.
    - no variable paid below `threshold`; linear from threshold→100%.
    - above 100% the marginal rate is multiplied by `accelerator`.
    - earnings capped at `cap`% of target variable.
    """
    base = target_total * base_pct / 100.0
    target_var = target_total - base
    a = att_pct
    if a <= threshold:
        var = 0.0
    elif a <= 100:
        # linear from threshold (0 payout) to 100 (full target variable)
        frac = (a - threshold) / (100 - threshold) if (100 - threshold) else 1.0
        var = target_var * frac
    else:
        over = (a - 100) / 100.0
        var = target_var * (1 + over * accelerator)
    cap_amt = target_var * cap / 100.0
    var = min(var, cap_amt)
    return base + var


def payout_curve(target_total, base_pct, threshold, accelerator, cap, points=41):
    xs = np.linspace(0, 200, points)
    ys = [payout_for_attainment(x, target_total, base_pct, threshold, accelerator, cap)
          for x in xs]
    return xs, ys


def simulate_population(n_reps, mean_att, std_att, target_total, base_pct,
                        threshold, accelerator, cap, avg_quota, seed=7):
    rng = np.random.default_rng(seed)
    att = rng.normal(mean_att, std_att, n_reps).clip(0, 220)
    payouts = np.array([payout_for_attainment(a, target_total, base_pct, threshold,
                                              accelerator, cap) for a in att])
    total_payout = payouts.sum()
    # revenue generated ~ attainment * quota
    revenue = (att / 100.0 * avg_quota).sum()
    cost_of_sales = total_payout / revenue * 100 if revenue else 0
    pct_above_target = float((att >= 100).mean() * 100)
    pct_below_threshold = float((att < threshold).mean() * 100)
    return {
        "att": att, "payouts": payouts,
        "avg_payout": float(payouts.mean()),
        "total_payout": float(total_payout),
        "revenue": float(revenue),
        "cost_of_sales": round(cost_of_sales, 1),
        "pct_above_target": round(pct_above_target, 1),
        "pct_below_threshold": round(pct_below_threshold, 1),
        "avg_attainment": round(float(att.mean()), 1),
    }


def ic_summary(sim, target_total, base_pct, threshold, accelerator, cap):
    cos = sim["cost_of_sales"]
    health = ("lean" if cos < 8 else ("healthy" if cos < 15 else "rich — review payout leverage"))
    return (
        f"At a {base_pct}/{100 - base_pct} base/variable split with a {threshold}% threshold, a "
        f"{accelerator:.1f}× accelerator above quota and a {cap}% cap, the simulated rep population "
        f"(avg attainment {sim['avg_attainment']}%) earns an average of **${sim['avg_payout']:,.0f}** "
        f"against a ${target_total:,.0f} target. Total payout is **${sim['total_payout']:,.0f}**, a "
        f"**{cos}% cost of sales** — {health}. **{sim['pct_above_target']}%** of reps clear quota and "
        f"**{sim['pct_below_threshold']}%** fall below the threshold (zero variable). "
        f"A well-calibrated plan pays ~60–70% of reps above threshold and keeps cost of sales in a "
        f"defensible band; tune threshold, accelerator and cap to shift cost and motivation accordingly."
    )
