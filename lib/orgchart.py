"""Org-chart rendering as Graphviz DOT strings (rendered client-side by st.graphviz_chart —
no system Graphviz binary and no extra Python dependency required)."""
import math

_DARK_NODE = 'style=filled, fontcolor="#EAF0FF", color="#8B6CFF", fillcolor="#1b2138", fontname="Helvetica"'
_ACCENT_NODE = 'style=filled, fontcolor="#06121f", color="#22D3EE", fillcolor="#22D3EE", fontname="Helvetica"'


def field_org_dot(team_structures, span_dm=8, dm_per_rm=5):
    """team_structures: list of {name, reps}. Returns a DOT org chart:
    National Sales Director → Team lead → Regional managers → District managers → Reps (counts)."""
    lines = ['digraph G {', 'graph [bgcolor="transparent", rankdir=TB, nodesep=0.3, ranksep=0.5];',
             f'node [shape=box, style=filled, fontcolor="#EAF0FF", color="#8B6CFF", '
             f'fillcolor="#1b2138", fontname="Helvetica", fontsize=11];',
             'edge [color="#5b6488"];']
    total_reps = sum(t["reps"] for t in team_structures)
    lines.append(f'NSD [label="National Sales Director\\n{total_reps} reps total", {_ACCENT_NODE}];')
    for i, t in enumerate(team_structures):
        reps = max(0, int(t["reps"]))
        dm = max(1, math.ceil(reps / span_dm)) if reps else 0
        rm = max(1, math.ceil(dm / dm_per_rm)) if dm else 0
        tn = f"team{i}"
        lines.append(f'{tn} [label="{t["name"]}\\nLead", fillcolor="#23314f", color="#22D3EE"];')
        lines.append(f'NSD -> {tn};')
        if rm:
            rmn = f"rm{i}"
            lines.append(f'{rmn} [label="{rm} Regional Manager(s)"];')
            lines.append(f'{tn} -> {rmn};')
            dmn = f"dm{i}"
            lines.append(f'{dmn} [label="{dm} District Manager(s)"];')
            lines.append(f'{rmn} -> {dmn};')
            rn = f"rep{i}"
            lines.append(f'{rn} [label="{reps} Sales Reps", fillcolor="#143042", color="#22D3EE"];')
            lines.append(f'{dmn} -> {rn};')
    lines.append('}')
    return "\n".join(lines)


def org_counts(reps, span_dm=8, dm_per_rm=5):
    dm = math.ceil(reps / span_dm) if reps else 0
    rm = math.ceil(dm / dm_per_rm) if dm else 0
    return {"reps": int(reps), "district_mgrs": dm, "regional_mgrs": rm,
            "managers": dm + rm, "mgr_ratio": round((dm + rm) / reps, 2) if reps else 0}
