# SEDE queries

Stack Exchange Data Explorer: https://data.stackexchange.com/stackoverflow/queries

## How SEDE actually works (read before pulling)

- Each query is **capped at ~50,000 rows**. Our monthly panel is well under this; the question text sample is also fine if batched by quarter+tag.
- SEDE does **not** support list parameters. You run each query **once per tag**, swapping the `##Tag##` parameter in the UI.
- The `Posts.Tags` column is a **string** like `<python><pandas><dataframe>`, not a relational table. Filter with `LIKE '%<tag>%'`. Use angle brackets to avoid `<javascript>` matching `<typescript>`.
- Results download as CSV from the "Download CSV" button below the results table.
- SEDE caches queries by parameter values; you'll see cached results return instantly.

## Pull procedure (the painful part)

For each of the 14 tags below, run **both** queries and save the CSV with a predictable name.

**Tags to pull:**

LLM-friendly: `python`, `javascript`, `reactjs`, `pandas`, `html`, `css`, `sql`
LLM-unfriendly: `assembly`, `verilog`, `vhdl`, `cobol`, `fortran`, `embedded`, `kernel`

**File naming convention** (used by `src/load.py`):
```
data/raw/monthly_{tag}.csv
data/raw/sample_{tag}.csv
```

Example: `data/raw/monthly_python.csv`, `data/raw/sample_reactjs.csv`

## Splitting the work

14 tags × 2 queries = 28 CSVs. Divide across the team:
- Person A: python, javascript, reactjs (3 tags = 6 CSVs)
- Person B: pandas, html, css (3 tags = 6 CSVs)
- Person C: sql, assembly, verilog (3 tags = 6 CSVs)
- Person D: vhdl, cobol, fortran (3 tags = 6 CSVs)
- Person E: embedded, kernel (2 tags = 4 CSVs)

Should take ~30 minutes total per person.

## Files

- `monthly_panel.sql` — Query 1: monthly aggregates per tag.
- `question_sample.sql` — Query 2: random sample of question bodies.
