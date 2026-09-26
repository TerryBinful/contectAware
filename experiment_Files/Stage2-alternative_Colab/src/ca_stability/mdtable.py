"""Dependency-free DataFrame -> Markdown table (avoids requiring `tabulate`)."""
from __future__ import annotations

import math

import pandas as pd


def _fmt(v, floatfmt: str) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        if math.isnan(v):
            return "—"
        return format(v, floatfmt)
    return str(v).replace("|", "\\|")


def df_to_markdown(df: pd.DataFrame, floatfmt: str = ".4g", index: bool = False) -> str:
    if index:
        df = df.reset_index()
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for row in df.itertuples(index=False):
        out.append("| " + " | ".join(_fmt(v, floatfmt) for v in row) + " |")
    return "\n".join(out)
