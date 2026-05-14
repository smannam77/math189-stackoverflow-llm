"""
Generate synthetic CSVs that match the shape of the SEDE output, so the
EDA pipeline can be tested end-to-end before the real data is pulled.

Run from repo root:
    python src/make_synthetic_data.py
"""
import numpy as np
import pandas as pd
from pathlib import Path

from src.load import LLM_FRIENDLY, LLM_UNFRIENDLY, TREATMENT_DATE

rng = np.random.default_rng(42)
OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)

months = pd.date_range("2019-01-01", "2024-12-01", freq="MS")
n = len(months)
post = (months >= TREATMENT_DATE).astype(int)

# Per-tag baseline volume (rough order of magnitude for SO)
baselines = {
    "python": 40000, "javascript": 35000, "reactjs": 8000, "pandas": 6000,
    "html": 5000, "css": 4000, "sql": 7000,
    "assembly": 400, "verilog": 150, "vhdl": 120, "cobol": 60,
    "fortran": 200, "embedded": 300, "kernel": 250,
}

for tag in LLM_FRIENDLY + LLM_UNFRIENDLY:
    base = baselines[tag]
    is_friendly = tag in LLM_FRIENDLY

    # Mild secular decline (SO has been declining since ~2015)
    trend = np.linspace(1.0, 0.85, n)
    # Treatment effect: -40% for friendly, -5% for unfriendly
    effect = 1 - (0.40 if is_friendly else 0.05) * post
    # Noise
    noise = rng.normal(1.0, 0.07, n)

    n_questions = (base * trend * effect * noise).clip(min=10).astype(int)

    df = pd.DataFrame({
        "month": months,
        "n_questions": n_questions,
        "avg_body_len": rng.normal(900 + 80 * post * is_friendly, 60, n),
        "avg_score": rng.normal(1.5, 0.3, n),
        "accept_rate": rng.normal(0.55 + 0.05 * post * is_friendly, 0.03, n).clip(0, 1),
        "answered_rate": rng.normal(0.75, 0.05, n).clip(0, 1),
        "avg_hours_to_first_answer": rng.normal(2.0 + 0.5 * post * is_friendly, 0.4, n).clip(0.1),
        "unique_askers": (n_questions * rng.normal(0.85, 0.02, n)).astype(int),
        "first_time_askers": (n_questions * rng.normal(0.25 - 0.08 * post * is_friendly, 0.02, n)).clip(0).astype(int),
    })
    df.to_csv(OUT / f"monthly_{tag}.csv", index=False)

print(f"Wrote {len(LLM_FRIENDLY) + len(LLM_UNFRIENDLY)} synthetic monthly_*.csv files to {OUT}")
