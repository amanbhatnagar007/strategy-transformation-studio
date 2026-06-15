import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="Spans & Layers Optimizer", page_icon="🪜", layout="wide")
page_header("🪜 Spans & Layers Optimizer",
            "Simulate a de-layering: widen spans of control, remove management layers, and size the "
            "annualized cost saving — with a realization haircut applied so the number stays honest.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

REALIZATION = 0.55  # not every removed role converts to cash; some redeploy

with st.sidebar:
    st.header("Current organization")
    headcount = st.number_input("Total headcount (FTEs)", 50, 500000, 6000, step=50)
    cur_layers = st.slider("Current layers (CEO → front line)", 4, 14, 9)
    cur_span = st.slider("Current avg span of control", 2.0, 10.0, 4.5, 0.5)
    st.header("Target")
    tgt_span = st.slider("Target avg span of control", 4.0, 12.0, 7.0, 0.5)
    mgr_cost = st.number_input("Avg fully-loaded manager cost ($k)", 50, 1000, 160, step=10)

if tgt_span <= cur_span:
    st.warning("Target span is not wider than current — widen the target span to model a de-layering.")

# Managers ≈ headcount / span (every span-many reports needs a manager).
cur_managers = round(headcount / max(cur_span, 1.5))
tgt_managers = round(headcount / max(tgt_span, 1.5))
roles_removed = max(0, cur_managers - tgt_managers)

# Layers implied by span: layers ≈ log(headcount)/log(span).
import math
def implied_layers(hc, span):
    return max(1, round(math.log(max(hc, 2)) / math.log(max(span, 1.5))))
tgt_layers = min(cur_layers, implied_layers(headcount, tgt_span))
layers_removed = max(0, cur_layers - tgt_layers)

gross_saving = roles_removed * mgr_cost / 1000.0  # $M
net_saving = gross_saving * REALIZATION           # $M

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">~{roles_removed:,}</div><div class="l">Mgmt roles removed</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{layers_removed}</div><div class="l">Layers removed</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${net_saving:,.1f}M</div><div class="l">Net annual saving</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🪜 Before / after org", "💰 Savings", "📋 Executive summary"])

def pyramid(layers, span, hc):
    """Approx headcount per layer, top→bottom, normalized to total headcount."""
    raw = [span ** i for i in range(layers)]
    tot = sum(raw)
    return [round(r / tot * hc) for r in raw]

with t1:
    st.markdown("#### Organization shape: current vs target")
    cur_p = pyramid(cur_layers, cur_span, headcount)
    tgt_p = pyramid(tgt_layers, tgt_span, headcount)
    n = max(len(cur_p), len(tgt_p))
    labels = [f"Layer {i+1}" for i in range(n)]
    cur_p += [0] * (n - len(cur_p))
    tgt_p += [0] * (n - len(tgt_p))
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Current", y=labels, x=cur_p, orientation="h",
                         marker_color="#8B6CFF", text=[f"{v:,}" if v else "" for v in cur_p],
                         textposition="outside"))
    fig.add_trace(go.Bar(name="Target", y=labels, x=tgt_p, orientation="h",
                         marker_color="#22D3EE", text=[f"{v:,}" if v else "" for v in tgt_p],
                         textposition="outside"))
    fig.update_layout(template="plotly_dark", height=360, barmode="group",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis=dict(autorange="reversed"), xaxis_title="Headcount (approx)",
                      legend=dict(orientation="h", y=-0.2), margin=dict(l=10, r=30, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass(f'<div style="color:#aab4d6;font-size:.85rem">Moving from a span of <b style="color:#fff">{cur_span}</b> '
          f'to <b style="color:#fff">{tgt_span}</b> flattens the org from ~{cur_layers} to ~{tgt_layers} layers. '
          'Layer headcounts are geometric approximations from span — they illustrate the shape change, not a '
          'role-by-role plan.</div>')

with t2:
    st.markdown("#### Annualized cost saving")
    fig = go.Figure(go.Bar(
        x=["Gross saving", f"Net saving (×{REALIZATION:g})"],
        y=[round(gross_saving, 1), round(net_saving, 1)],
        marker_color=["#22D3EE", "#8B6CFF"],
        text=[f"${gross_saving:,.1f}M", f"${net_saving:,.1f}M"], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Annual saving ($M)",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pd.DataFrame([
        {"Metric": "Current managers", "Value": f"~{cur_managers:,}"},
        {"Metric": "Target managers", "Value": f"~{tgt_managers:,}"},
        {"Metric": "Roles removed", "Value": f"~{roles_removed:,}"},
        {"Metric": "Layers removed", "Value": layers_removed},
        {"Metric": "Gross saving ($M)", "Value": round(gross_saving, 1)},
        {"Metric": f"Realization factor", "Value": REALIZATION},
        {"Metric": "Net saving ($M)", "Value": round(net_saving, 1)},
    ]), use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### Board-ready read")
    summary = (
        f"Widening average span from <b>{cur_span}</b> to <b>{tgt_span}</b> removes ~<b>{roles_removed:,} "
        f"management roles</b> and flattens the organization by <b>{layers_removed} layer(s)</b> "
        f"(~{cur_layers} → ~{tgt_layers}). At a fully-loaded manager cost of ${mgr_cost}k, that is "
        f"~${gross_saving:,.1f}M gross. Applying a <b>{int(REALIZATION*100)}% realization factor</b> — "
        f"because not every removed role converts to cash; some headcount redeploys or backfills — the "
        f"defensible net annual saving is ~<b>${net_saving:,.1f}M</b>. Flatter structures also speed "
        f"decisions and clarify accountability. These are directional heuristics; confirm spans and "
        f"redeployment assumptions against the actual org chart before committing."
    )
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{summary}</div>')
    csv = pd.DataFrame([
        {"Item": "Headcount", "Value": headcount},
        {"Item": "Current span", "Value": cur_span},
        {"Item": "Target span", "Value": tgt_span},
        {"Item": "Current layers", "Value": cur_layers},
        {"Item": "Target layers", "Value": tgt_layers},
        {"Item": "Layers removed", "Value": layers_removed},
        {"Item": "Current managers", "Value": cur_managers},
        {"Item": "Target managers", "Value": tgt_managers},
        {"Item": "Roles removed", "Value": roles_removed},
        {"Item": "Manager cost ($k)", "Value": mgr_cost},
        {"Item": "Gross saving ($M)", "Value": round(gross_saving, 1)},
        {"Item": "Realization factor", "Value": REALIZATION},
        {"Item": "Net saving ($M)", "Value": round(net_saving, 1)},
    ])
    st.download_button("⬇ Download de-layering model (CSV)", csv.to_csv(index=False),
                       file_name="spans_layers.csv", mime="text/csv")

st.caption("AI-assisted heuristic model for de-layering framing. Directional planning tool. "
           f"For a transformation engagement: {PROFILE['email']}.")
