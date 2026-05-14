# LLMs and Stack Overflow — MATH 189 Group 9

How the public release of ChatGPT (Nov 30, 2022) reshaped question-asking on Stack Overflow.

**Team:** Dane Kosky · Shahmun Jafri · Srikar Mannam · Zhentao Lei · Zubin Sannakkayala

## Research question

After the public release of ChatGPT, did "easy" questions disappear from LLM-friendly Stack Overflow tags faster than from LLM-unfriendly tags, and did the questions that remained become measurably more complex?

## Design

Difference-in-differences with two tag groups over Jan 2019 – Dec 2024.

| Group | Tags |
|---|---|
| LLM-friendly (treatment) | python, javascript, reactjs, pandas, html, css, sql |
| LLM-unfriendly (control) | assembly, verilog, vhdl, cobol, fortran, embedded, kernel |

Treatment date: **December 2022** (first full month after ChatGPT's Nov 30, 2022 release).

## Repo layout

```
.
├── sql/                  Parameterized SEDE queries
├── data/
│   ├── raw/              CSVs straight from SEDE (gitignored)
│   ├── interim/          Combined panels
│   └── processed/        Analysis-ready datasets
├── notebooks/            EDA, modeling, write-up
├── src/                  Shared helpers (load, features, plots)
├── reports/figures/      Figures used in the final write-up
└── docs/                 Proposal and final report
```

## Getting started (Colab)

1. Open any notebook in `notebooks/` in Colab.
2. The first cell clones this repo and installs requirements.
3. Place the raw SEDE CSVs in `data/raw/` (see `sql/README.md` for the exact pull procedure).

For local Jupyter:
```bash
pip install -r requirements.txt
jupyter lab
```

## Workflow rules

- One branch per person: `work/<your-name>`. Merge to `main` via PR; no direct pushes.
- Notebook outputs are stripped before commit (`nbstripout` if running locally).
- Raw CSVs are gitignored. Share via Google Drive or re-pull from SEDE.
- Shared code goes in `src/`, not duplicated across notebooks.

## Notebooks

| Notebook | Owner | Purpose |
|---|---|---|
| `01_data_pull_log.ipynb` | TBD | Document SEDE pull procedure |
| `02_eda_volume.ipynb` | TBD | Time-series and heatmaps of question volume |
| `03_eda_distributions.ipynb` | TBD | Body length, accept rate, time-to-first-answer |
| `04_pretrend_check.ipynb` | TBD | Critical: parallel trends diagnostic for DiD |
| `05_text_features.ipynb` | TBD | Difficulty score, readability, code blocks |
| `06_cohort_retention.ipynb` | TBD | New-user retention curves |
