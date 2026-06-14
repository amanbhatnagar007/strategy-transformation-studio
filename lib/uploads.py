"""Reusable data-upload framework: template download, upload, and validation.

Pattern for every data-driven app:
    schema = ColumnSchema([...])
    df = data_input(schema, sample_df)   # renders template download + uploader + demo toggle
    if df is not None: ... analyze real data ...
"""
from __future__ import annotations
import io
from dataclasses import dataclass
import pandas as pd
import streamlit as st


@dataclass
class Col:
    name: str
    kind: str               # "num" | "int" | "text" | "pct"
    desc: str
    example: str = ""
    required: bool = True    # optional columns unlock features but never block the run


class ColumnSchema:
    def __init__(self, cols: list[Col]):
        self.cols = cols

    @property
    def names(self):
        return [c.name for c in self.cols]

    @property
    def required(self):
        return [c for c in self.cols if c.required]

    @property
    def optional(self):
        return [c for c in self.cols if not c.required]

    def template_df(self, sample_rows: list[dict] | None = None) -> pd.DataFrame:
        # Template shows ALL columns (required + optional) so users see the full shape.
        if sample_rows:
            present = [n for n in self.names if n in pd.DataFrame(sample_rows).columns]
            return pd.DataFrame(sample_rows)[present]
        return pd.DataFrame([{c.name: c.example for c in self.cols}])

    def validate(self, df: pd.DataFrame):
        """Return (clean_df, errors, warnings, present_optional).
        Only REQUIRED columns block; optional ones are kept if present, noted if absent.
        Never fabricates rows."""
        errors, warnings = [], []
        missing_req = [c.name for c in self.required if c.name not in df.columns]
        if missing_req:
            errors.append(f"Missing required column(s): {', '.join(missing_req)}. "
                          "Download the template to see the exact headers.")
            return None, errors, warnings, []
        present_opt = [c.name for c in self.optional if c.name in df.columns]
        absent_opt = [c.name for c in self.optional if c.name not in df.columns]
        if absent_opt:
            warnings.append("Optional columns not provided (some features limited): "
                            + ", ".join(absent_opt))
        keep = [c for c in self.cols if c.name in df.columns]
        df = df[[c.name for c in keep]].copy()
        for c in keep:
            if c.kind in ("num", "int", "pct"):
                coerced = pd.to_numeric(df[c.name], errors="coerce")
                bad = int(coerced.isna().sum())
                if bad and c.required:
                    warnings.append(f"'{c.name}': {bad} non-numeric value(s) dropped.")
                df[c.name] = coerced
                if c.kind == "int":
                    df[c.name] = df[c.name].round()
        before = len(df)
        req_numeric = [c.name for c in self.required if c.kind in ("num", "int", "pct")]
        df = df.dropna(subset=req_numeric) if req_numeric else df
        if len(df) < before:
            warnings.append(f"{before - len(df)} row(s) missing required numbers were dropped.")
        if df.empty:
            errors.append("No valid rows after cleaning — check the file against the template.")
            return None, errors, warnings, present_opt
        return df, errors, warnings, present_opt


def _schema_help(schema: ColumnSchema):
    def row(c):
        badge = ("<span style='color:#22D3EE;font-size:.7rem'>required</span>" if c.required
                 else "<span style='color:#9AA6CC;font-size:.7rem'>optional</span>")
        return (f"<tr><td style='padding:3px 10px 3px 0;color:#c4b5ff'>{c.name}</td>"
                f"<td style='padding:3px 10px 3px 0'>{badge}</td>"
                f"<td style='padding:3px 10px 3px 0;color:#9AA6CC'>{c.kind}</td>"
                f"<td style='padding:3px 0;color:#aab4d6'>{c.desc}</td></tr>")
    rows = "".join(row(c) for c in schema.cols)
    st.markdown(
        "<div style='font-size:.83rem'><b style='color:#fff'>Columns</b> "
        "<span style='color:#9AA6CC'>— required columns must be present; optional ones unlock extra analysis</span>"
        f"<table style='margin-top:.4rem'>{rows}</table></div>", unsafe_allow_html=True)


def data_input(schema: ColumnSchema, sample_rows: list[dict], demo_label="Use demo data",
               key="upload"):
    """Render the standard upload UX. Returns a validated DataFrame (real or demo)."""
    template = schema.template_df(sample_rows)
    c1, c2 = st.columns([1, 1])
    with c1:
        csv = template.to_csv(index=False).encode()
        st.download_button("⬇ Download CSV template", csv, file_name=f"{key}_template.csv",
                           mime="text/csv", use_container_width=True)
    with c2:
        use_demo = st.toggle(demo_label, value=True, key=f"{key}_demo")

    with st.expander("What the file should contain"):
        _schema_help(schema)

    if use_demo:
        df, _, _, _ = schema.validate(pd.DataFrame(sample_rows))
        st.caption(f"Showing demo data ({len(df)} rows). Turn off the toggle to upload your own.")
        return df

    up = st.file_uploader("Upload your CSV or Excel (matching the template)",
                          type=["csv", "xlsx"], key=f"{key}_file")
    if up is None:
        st.info("Upload a file, or switch on demo data to explore the app.")
        return None
    try:
        raw = pd.read_excel(up) if up.name.endswith("xlsx") else pd.read_csv(up)
    except Exception as e:
        st.error(f"Could not read the file: {e}")
        return None
    df, errors, warnings, present_opt = schema.validate(raw)
    for w in warnings:
        st.warning(w)
    for e in errors:
        st.error(e)
    if df is not None:
        extra = f" · optional columns used: {', '.join(present_opt)}" if present_opt else ""
        st.success(f"Loaded {len(df)} valid rows{extra}.")
    return df
