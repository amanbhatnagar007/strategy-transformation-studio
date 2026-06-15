import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.uploads import ColumnSchema, Col, data_input

st.set_page_config(page_title="Omnichannel Optimizer", page_icon="📡", layout="wide")
page_header("📡 Omnichannel Optimizer",
            "Optimize the promotional channel mix across field, digital and rep-triggered touches. "
            "A saturating response model reallocates budget to where the next dollar buys the most conversions.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

ACCENT, ACCENT2 = "#8B6CFF", "#22D3EE"


def conversions(spend, cpt, coef):
    """Saturating response: touches = spend/cpt; conversions = touches saturated by coef.
    Diminishing returns via 1 - exp(-coef * touches / scale)."""
    spend = np.asarray(spend, dtype=float)
    cpt = max(float(cpt), 1e-6)
    touches = spend / cpt
    cap = 0.5 + coef * 4.0  # response coefficient sets the saturation ceiling (conv per 1k touches scale)
    return cap * (1 - np.exp(-touches / 4000.0))


def optimize(channels, budget, step=None):
    """Greedy marginal-return allocation across channels for a fixed budget."""
    names = [c["channel"] for c in channels]
    if step is None:
        step = max(budget / 400.0, 1.0)
    alloc = {n: 0.0 for n in names}
    spent = 0.0
    cfg = {c["channel"]: c for c in channels}
    while spent + step <= budget + 1e-9:
        best, best_gain = None, -1.0
        for n in names:
            c = cfg[n]
            cur = conversions(alloc[n], c["cost_per_touch"], c["response_coef"])
            nxt = conversions(alloc[n] + step, c["cost_per_touch"], c["response_coef"])
            gain = float(nxt - cur)
            if gain > best_gain:
                best, best_gain = n, gain
        if best is None or best_gain <= 0:
            break
        alloc[best] += step
        spent += step
    return alloc


def channel_table(channels, alloc):
    rows = []
    for c in channels:
        n = c["channel"]
        conv = float(conversions(alloc[n], c["cost_per_touch"], c["response_coef"]))
        touches = alloc[n] / max(c["cost_per_touch"], 1e-6)
        rows.append({"Channel": n, "Allocated spend ($)": round(alloc[n]),
                     "Touches": round(touches), "Conversions": round(conv, 1),
                     "Cost / conversion ($)": round(alloc[n] / conv, 0) if conv > 0 else np.nan})
    return pd.DataFrame(rows)


DEFAULTS = [
    ("Field", 18.0, 0.55), ("Email", 0.8, 0.30), ("Web/portal", 1.5, 0.35),
    ("Webinars", 6.0, 0.45), ("Display", 2.5, 0.20), ("Rep-triggered", 4.0, 0.50),
]

with st.sidebar:
    st.header("Budget")
    budget = st.number_input("Total promotional budget ($)", 10000, 50_000_000, 1_000_000, step=10000)
    st.header("Channel economics")
    st.caption("Cost per touch and a diminishing-returns response coefficient (higher = more responsive).")
    sb_channels = []
    cur_spend = {}
    for name, cpt0, coef0 in DEFAULTS:
        with st.expander(name, expanded=(name == "Field")):
            cpt = st.number_input(f"{name} · cost per touch ($)", 0.1, 500.0, cpt0, step=0.1, key=f"cpt_{name}")
            coef = st.slider(f"{name} · response coefficient", 0.05, 1.0, coef0, 0.05, key=f"coef_{name}")
            cur = st.number_input(f"{name} · current spend ($)", 0, 50_000_000,
                                  int(budget / len(DEFAULTS)), step=1000, key=f"cur_{name}")
        sb_channels.append({"channel": name, "cost_per_touch": cpt, "response_coef": coef})
        cur_spend[name] = float(cur)

t1, tU, t2, t3 = st.tabs(["🎛️ Optimize mix", "📤 Upload your data", "📈 Response curves", "📋 Executive summary"])


def render(channels, current_alloc, budget, key):
    opt_alloc = optimize(channels, budget)
    cur_tbl = channel_table(channels, current_alloc)
    opt_tbl = channel_table(channels, opt_alloc)
    tot_conv_cur = cur_tbl["Conversions"].sum()
    tot_conv_opt = opt_tbl["Conversions"].sum()
    opt_spend_total = sum(opt_alloc.values())
    cpc = opt_spend_total / tot_conv_opt if tot_conv_opt > 0 else float("nan")
    top = opt_tbl.sort_values("Conversions", ascending=False).iloc[0]["Channel"]
    lift = (tot_conv_opt / tot_conv_cur - 1) * 100 if tot_conv_cur > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="glass metric"><div class="v">{tot_conv_opt:,.0f}</div><div class="l">Optimized conversions</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="glass metric"><div class="v">${cpc:,.0f}</div><div class="l">Blended cost / conversion</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="glass metric"><div class="v">{top}</div><div class="l">Top recommended channel</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="glass metric"><div class="v">{lift:+.0f}%</div><div class="l">Conversion lift vs current</div></div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Current", x=cur_tbl["Channel"], y=cur_tbl["Allocated spend ($)"], marker_color=ACCENT))
    fig.add_trace(go.Bar(name="Optimized", x=opt_tbl["Channel"], y=opt_tbl["Allocated spend ($)"], marker_color=ACCENT2))
    fig.update_layout(template="plotly_dark", height=340, barmode="group",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_title="Spend ($)", margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True, key=f"alloc_{key}")
    st.markdown("##### Recommended allocation")
    st.dataframe(opt_tbl, use_container_width=True, hide_index=True)
    return opt_tbl, opt_alloc, tot_conv_cur, tot_conv_opt, top, cpc, lift, channels, budget


def curves_chart(channels, budget, key):
    xs = np.linspace(0, budget, 60)
    fig = go.Figure()
    palette = [ACCENT, ACCENT2, "#EC4899", "#F59E0B", "#34D399", "#60A5FA"]
    for i, c in enumerate(channels):
        ys = conversions(xs, c["cost_per_touch"], c["response_coef"])
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=c["channel"],
                                 line=dict(color=palette[i % len(palette)], width=2.5)))
    fig.update_layout(template="plotly_dark", height=380, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Spend in channel ($)",
                      yaxis_title="Conversions (saturating)", margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True, key=f"curves_{key}")


def summary_block(opt_tbl, tot_cur, tot_opt, top, cpc, lift, channels, budget, key):
    lo = opt_tbl.sort_values("Conversions").iloc[0]["Channel"]
    txt = (f"On a <b>${budget:,.0f}</b> budget across {len(channels)} channels, a marginal-return reallocation "
           f"lifts modeled conversions from <b>{tot_cur:,.0f}</b> to <b>{tot_opt:,.0f}</b> "
           f"(<b>{lift:+.0f}%</b>) at a blended <b>${cpc:,.0f}</b> per conversion. "
           f"<b>{top}</b> earns the largest share because its cost-per-touch and response coefficient deliver the "
           f"strongest marginal return; <b>{lo}</b> saturates fastest and should be capped. "
           f"Assumptions: each channel follows a saturating curve (conversions = ceiling·(1−e^(−touches/4000)), "
           f"ceiling = 0.5 + 4·coefficient). Figures are directional heuristics for planning, not a media-buy guarantee.")
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{txt}</div>')
    st.download_button("⬇ Download optimized mix (CSV)", opt_tbl.to_csv(index=False),
                       file_name="omnichannel_optimized.csv", mime="text/csv", key=f"dl_{key}")


with t1:
    st.markdown("#### Reallocate the budget to maximize conversions")
    res = render(sb_channels, cur_spend, budget, "sidebar")
    st.session_state["_omni_sidebar"] = res

with tU:
    st.markdown("#### Upload your channel plan to optimize against your own economics")
    st.caption("The model only analyzes the channels you provide — it never invents channels.")
    schema = ColumnSchema([
        Col("channel", "text", "Channel name", "Field"),
        Col("spend", "num", "Current spend in this channel ($)", "160000"),
        Col("cost_per_touch", "num", "Cost per touch/impression ($)", "18"),
        Col("response_coef", "pct", "Response coefficient 0.05–1.0 (higher = more responsive)", "0.55"),
    ])
    demo_rows = [{"channel": n, "spend": round(budget / len(DEFAULTS)),
                  "cost_per_touch": cpt, "response_coef": coef} for n, cpt, coef in DEFAULTS]
    udf = data_input(schema, demo_rows, key="omni")
    if udf is not None and not udf.empty:
        u_channels = [{"channel": str(r["channel"]), "cost_per_touch": float(r["cost_per_touch"]),
                       "response_coef": float(min(max(r["response_coef"], 0.05), 1.0))}
                      for _, r in udf.iterrows()]
        u_current = {str(r["channel"]): float(r["spend"]) for _, r in udf.iterrows()}
        u_budget = float(udf["spend"].sum())
        st.caption(f"Optimizing against your total current spend of ${u_budget:,.0f}.")
        ures = render(u_channels, u_current, u_budget, "upload")
        st.markdown("##### Response curves (your data)")
        curves_chart(u_channels, u_budget, "upload")
        summary_block(ures[0], ures[2], ures[3], ures[4], ures[5], ures[6],
                      u_channels, u_budget, "upload")

with t2:
    st.markdown("#### Saturating response curves by channel")
    curves_chart(sb_channels, budget, "sidebar")
    glass('<div style="color:#aab4d6;font-size:.85rem">Each curve flattens as a channel saturates. The optimizer '
          'walks budget in small steps to whichever channel offers the highest next-dollar conversion gain, so '
          'no single channel is over-funded past its point of diminishing returns.</div>')

with t3:
    st.markdown("#### Board-ready read")
    r = st.session_state.get("_omni_sidebar")
    if r:
        summary_block(r[0], r[2], r[3], r[4], r[5], r[6], sb_channels, budget, "sidebar")

st.caption("AI-assisted heuristic channel-mix model — directional planning support, not a media-buy guarantee. "
           f"For a tailored engagement: {PROFILE['email']}.")
