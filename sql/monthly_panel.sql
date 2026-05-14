-- ============================================================
-- Query 1: Monthly aggregate panel for one tag
-- Stack Exchange Data Explorer (T-SQL dialect)
--
-- Parameter (set in SEDE UI):
--   ##Tag:string##   e.g. "python", "assembly"
--
-- Output: one row per month, Jan 2019 - Dec 2024
-- Save as: data/raw/monthly_<tag>.csv
-- ============================================================

WITH q AS (
  SELECT
    p.Id,
    p.CreationDate,
    p.Score,
    p.Body,
    p.AcceptedAnswerId,
    p.OwnerUserId,
    p.AnswerCount
  FROM Posts p
  WHERE p.PostTypeId = 1                                  -- 1 = question
    AND p.Tags LIKE '%<' + ##Tag:string## + '>%'          -- angle brackets prevent partial matches
    AND p.CreationDate >= '2019-01-01'
    AND p.CreationDate <  '2025-01-01'
),

-- Time of the FIRST answer for each question (NULL if never answered)
first_answer AS (
  SELECT
    a.ParentId AS QuestionId,
    MIN(a.CreationDate) AS FirstAnswerDate
  FROM Posts a
  WHERE a.PostTypeId = 2                                  -- 2 = answer
    AND a.ParentId IN (SELECT Id FROM q)
  GROUP BY a.ParentId
),

-- Mark whether each asker is posting for the first time in this question
-- (their first-ever question on the whole site is this one)
first_time_asker AS (
  SELECT
    q.Id AS QuestionId,
    CASE
      WHEN q.CreationDate = (
        SELECT MIN(p2.CreationDate)
        FROM Posts p2
        WHERE p2.PostTypeId = 1 AND p2.OwnerUserId = q.OwnerUserId
      ) THEN 1 ELSE 0
    END AS IsFirstTimeAsker
  FROM q
  WHERE q.OwnerUserId IS NOT NULL
)

SELECT
  DATEFROMPARTS(YEAR(q.CreationDate), MONTH(q.CreationDate), 1) AS month,
  COUNT(*)                                                  AS n_questions,
  AVG(CAST(LEN(q.Body) AS FLOAT))                           AS avg_body_len,
  AVG(CAST(q.Score AS FLOAT))                               AS avg_score,
  AVG(CASE WHEN q.AcceptedAnswerId IS NOT NULL
           THEN 1.0 ELSE 0.0 END)                           AS accept_rate,
  AVG(CASE WHEN q.AnswerCount > 0 THEN 1.0 ELSE 0.0 END)    AS answered_rate,
  AVG(CAST(DATEDIFF(MINUTE, q.CreationDate, fa.FirstAnswerDate) AS FLOAT) / 60.0) AS avg_hours_to_first_answer,
  COUNT(DISTINCT q.OwnerUserId)                             AS unique_askers,
  SUM(CAST(fta.IsFirstTimeAsker AS INT))                    AS first_time_askers
FROM q
LEFT JOIN first_answer fa ON fa.QuestionId = q.Id
LEFT JOIN first_time_asker fta ON fta.QuestionId = q.Id
GROUP BY DATEFROMPARTS(YEAR(q.CreationDate), MONTH(q.CreationDate), 1)
ORDER BY month;
