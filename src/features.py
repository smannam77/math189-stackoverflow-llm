"""
Feature extraction for the question text sample.

Difficulty score components:
    - word_count        : words in body (HTML stripped)
    - n_code_blocks     : count of <pre><code> blocks
    - has_error         : regex match for stack traces / error messages
    - n_tags            : number of tags on the question
    - fk_grade          : Flesch-Kincaid grade level on body text
"""
from __future__ import annotations
import re
import pandas as pd
from bs4 import BeautifulSoup

try:
    import textstat
    _HAS_TEXTSTAT = True
except ImportError:
    _HAS_TEXTSTAT = False


# Common error / traceback patterns across languages
ERROR_PATTERNS = [
    r"Traceback \(most recent call last\)",
    r"\b[A-Z][a-zA-Z]*Error\b",          # Python: ValueError, KeyError, etc.
    r"\b[A-Z][a-zA-Z]*Exception\b",      # Java/C#: NullPointerException, etc.
    r"Uncaught \w+",                     # JavaScript
    r"undefined reference to",           # C/C++ linker
    r"segmentation fault",               # C
    r"syntax error",
    r"\bat line \d+",
    r"^\s+at\s+\S+\(",                   # JS/Java stack frame
]
_ERROR_RE = re.compile("|".join(ERROR_PATTERNS), re.IGNORECASE | re.MULTILINE)


def strip_html(html: str) -> tuple[str, int]:
    """Return (plain_text, n_code_blocks)."""
    if not isinstance(html, str):
        return "", 0
    soup = BeautifulSoup(html, "html.parser")
    n_code = len(soup.find_all("pre"))
    text = soup.get_text(separator=" ", strip=True)
    return text, n_code


def count_tags(tags_str: str) -> int:
    if not isinstance(tags_str, str):
        return 0
    return tags_str.count("<")


def has_error(text: str) -> int:
    if not isinstance(text, str) or not text:
        return 0
    return int(bool(_ERROR_RE.search(text)))


def fk_grade(text: str) -> float:
    if not _HAS_TEXTSTAT or not isinstance(text, str) or len(text.split()) < 5:
        return float("nan")
    try:
        return float(textstat.flesch_kincaid_grade(text))
    except Exception:
        return float("nan")


def add_features(sample: pd.DataFrame) -> pd.DataFrame:
    """Returns a copy of sample with feature columns appended."""
    df = sample.copy()
    plain, n_code = zip(*df["body_html"].map(strip_html))
    df["body_text"] = plain
    df["n_code_blocks"] = n_code
    df["word_count"] = df["body_text"].str.split().str.len().fillna(0).astype(int)
    df["n_tags"] = df["tags"].map(count_tags)
    df["has_error"] = df["body_text"].map(has_error)
    df["fk_grade"] = df["body_text"].map(fk_grade)
    return df


def difficulty_score(df: pd.DataFrame) -> pd.Series:
    """
    Composite difficulty score (z-scored sum of features, all signed so higher = harder).
    Compute on the full sample so the score is comparable across tags and periods.
    """
    cols = ["word_count", "n_code_blocks", "n_tags", "has_error", "fk_grade"]
    z = (df[cols] - df[cols].mean()) / df[cols].std(ddof=0)
    return z.sum(axis=1)
