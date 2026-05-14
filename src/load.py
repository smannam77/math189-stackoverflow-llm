"""
Load and combine SEDE per-tag CSVs into long-form analysis panels.

Usage in any notebook:
    from src.load import load_monthly_panel, load_question_sample, TAGS
    panel = load_monthly_panel("data/raw")
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

# Tag definitions — single source of truth for the whole project
LLM_FRIENDLY = ["python", "javascript", "reactjs", "pandas", "html", "css", "sql"]
LLM_UNFRIENDLY = ["assembly", "verilog", "vhdl", "cobol", "fortran", "embedded", "kernel"]
TAGS = LLM_FRIENDLY + LLM_UNFRIENDLY

TREATMENT_DATE = pd.Timestamp("2022-12-01")  # first full month after ChatGPT release


def _tag_group(tag: str) -> str:
    if tag in LLM_FRIENDLY:
        return "llm_friendly"
    if tag in LLM_UNFRIENDLY:
        return "llm_unfriendly"
    raise ValueError(f"Unknown tag: {tag}")


def load_monthly_panel(raw_dir: str | Path = "data/raw") -> pd.DataFrame:
    """
    Combine monthly_<tag>.csv files into one long-form panel.

    Returns columns:
        month, tag, group, post_chatgpt,
        n_questions, avg_body_len, avg_score, accept_rate,
        answered_rate, avg_hours_to_first_answer,
        unique_askers, first_time_askers
    """
    raw_dir = Path(raw_dir)
    frames = []
    missing = []

    for tag in TAGS:
        fp = raw_dir / f"monthly_{tag}.csv"
        if not fp.exists():
            missing.append(tag)
            continue
        df = pd.read_csv(fp, parse_dates=["month"])
        df["tag"] = tag
        df["group"] = _tag_group(tag)
        frames.append(df)

    if missing:
        print(f"[load_monthly_panel] WARNING: missing CSVs for tags: {missing}")
    if not frames:
        raise FileNotFoundError(f"No monthly_*.csv files found in {raw_dir}")

    panel = pd.concat(frames, ignore_index=True)
    panel["post_chatgpt"] = (panel["month"] >= TREATMENT_DATE).astype(int)
    panel["llm_friendly"] = (panel["group"] == "llm_friendly").astype(int)

    # Reorder for sanity
    front = ["month", "tag", "group", "llm_friendly", "post_chatgpt"]
    panel = panel[front + [c for c in panel.columns if c not in front]]
    return panel.sort_values(["tag", "month"]).reset_index(drop=True)


def load_question_sample(raw_dir: str | Path = "data/raw") -> pd.DataFrame:
    """
    Combine sample_<tag>.csv files into one long dataframe of question texts.

    Returns columns:
        question_id, created_at, quarter_start, title, body_html, tags,
        score, answer_count, has_accepted, tag, group, post_chatgpt
    """
    raw_dir = Path(raw_dir)
    frames = []
    missing = []

    for tag in TAGS:
        fp = raw_dir / f"sample_{tag}.csv"
        if not fp.exists():
            missing.append(tag)
            continue
        df = pd.read_csv(fp, parse_dates=["created_at", "quarter_start"])
        df["tag"] = tag
        df["group"] = _tag_group(tag)
        frames.append(df)

    if missing:
        print(f"[load_question_sample] WARNING: missing CSVs for tags: {missing}")
    if not frames:
        raise FileNotFoundError(f"No sample_*.csv files found in {raw_dir}")

    sample = pd.concat(frames, ignore_index=True)
    sample["post_chatgpt"] = (sample["created_at"] >= TREATMENT_DATE).astype(int)
    sample["llm_friendly"] = (sample["group"] == "llm_friendly").astype(int)
    return sample.reset_index(drop=True)


def panel_summary(panel: pd.DataFrame) -> pd.DataFrame:
    """Quick sanity check: row counts and date coverage per tag."""
    return (
        panel.groupby("tag")
        .agg(
            n_months=("month", "count"),
            first_month=("month", "min"),
            last_month=("month", "max"),
            total_questions=("n_questions", "sum"),
        )
        .reset_index()
    )
