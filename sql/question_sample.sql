-- ============================================================
-- Query 2: Random sample of question bodies for NLP
-- Stack Exchange Data Explorer (T-SQL dialect)
--
-- Parameters (set in SEDE UI):
--   ##Tag:string##           e.g. "python"
--   ##SamplePerQuarter:int## e.g. 50
--
-- Output: ~SamplePerQuarter * 24 quarters rows
-- Save as: data/raw/sample_<tag>.csv
--
-- Notes:
-- - Stratified by quarter so we get comparable samples across time.
-- - ABS(CHECKSUM(NEWID())) gives a pseudo-random ordering.
-- - Body contains HTML; we strip tags downstream in Python.
-- ============================================================

WITH q AS (
  SELECT
    p.Id,
    p.CreationDate,
    DATEFROMPARTS(
      YEAR(p.CreationDate),
      ((DATEPART(QUARTER, p.CreationDate) - 1) * 3) + 1,
      1
    ) AS quarter_start,
    p.Title,
    p.Body,
    p.Tags,
    p.Score,
    p.AnswerCount,
    p.AcceptedAnswerId
  FROM Posts p
  WHERE p.PostTypeId = 1
    AND p.Tags LIKE '%<' + ##Tag:string## + '>%'
    AND p.CreationDate >= '2019-01-01'
    AND p.CreationDate <  '2025-01-01'
),

ranked AS (
  SELECT
    q.*,
    ROW_NUMBER() OVER (
      PARTITION BY q.quarter_start
      ORDER BY ABS(CHECKSUM(NEWID()))
    ) AS rn
  FROM q
)

SELECT
  Id                                                      AS question_id,
  CreationDate                                            AS created_at,
  quarter_start,
  Title                                                   AS title,
  Body                                                    AS body_html,
  Tags                                                    AS tags,
  Score                                                   AS score,
  AnswerCount                                             AS answer_count,
  CASE WHEN AcceptedAnswerId IS NOT NULL
       THEN 1 ELSE 0 END                                  AS has_accepted
FROM ranked
WHERE rn <= ##SamplePerQuarter:int##
ORDER BY quarter_start, rn;
