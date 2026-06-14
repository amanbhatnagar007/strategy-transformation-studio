"""Shared 'action plan by tier' output: assign tiers, render action cards,
and offer a downloadable targeted list that ALWAYS includes the identifier."""
from __future__ import annotations
import pandas as pd
import streamlit as st


def assign_tier(value, tier_defs):
    """tier_defs: list of dicts {label, min, max, ...}; returns label whose [min,max) contains value."""
    for t in tier_defs:
        if t["min"] <= value < t["max"]:
            return t["label"]
    return tier_defs[-1]["label"]


def render_tiered_actions(df: pd.DataFrame, id_col: str, value_col: str, tier_defs: list[dict],
                          extra_cols: list[str] | None = None, key: str = "act",
                          value_fmt="{:.0f}"):
    """df must contain id_col and value_col. tier_defs: ordered list of
    {label, min, max, accent (hex), action (str), icon (str)}.
    Renders summary cards + per-tier action cards + per-tier downloadable lists (with id_col)."""
    extra_cols = extra_cols or []
    work = df.copy()
    work["__tier"] = work[value_col].apply(lambda v: assign_tier(v, tier_defs))

    # Summary cards
    cols = st.columns(len(tier_defs))
    for c, t in zip(cols, tier_defs):
        sub = work[work["__tier"] == t["label"]]
        c.markdown(
            f'<div class="glass metric" style="border-color:{t["accent"]}55">'
            f'<div class="v" style="color:{t["accent"]}">{len(sub)}</div>'
            f'<div class="l">{t["icon"]} {t["label"]}</div></div>', unsafe_allow_html=True)

    # Per-tier action cards + downloadable targeted lists
    for t in tier_defs:
        sub = work[work["__tier"] == t["label"]].sort_values(value_col, ascending=False)
        if sub.empty:
            continue
        st.markdown(
            f'<div class="glass" style="border-left:3px solid {t["accent"]};border-radius:0 16px 16px 0;margin-top:.6rem">'
            f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff">{t["icon"]} {t["label"]} '
            f'<span style="color:#9AA6CC;font-size:.8rem">· {len(sub)} records</span></div>'
            f'<div style="color:#c4b5ff;font-size:.9rem;margin-top:.3rem"><b>Action:</b> {t["action"]}</div></div>',
            unsafe_allow_html=True)
        show_cols = [id_col, value_col] + [c for c in extra_cols if c in sub.columns]
        with st.expander(f"View & download {t['label']} list ({len(sub)})"):
            st.dataframe(sub[show_cols], use_container_width=True, hide_index=True)
            st.download_button(
                f"⬇ {t['label']} targeted list (CSV)",
                sub[show_cols].to_csv(index=False),
                file_name=f"{key}_{t['label'].split()[0].lower()}_list.csv",
                mime="text/csv", key=f"{key}_{t['label']}_dl")
    return work
