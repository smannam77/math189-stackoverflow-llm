"""
Shared plotting style and helpers so every notebook produces consistent figures.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd

from src.load import TREATMENT_DATE, LLM_FRIENDLY, LLM_UNFRIENDLY


GROUP_COLORS = {
    "llm_friendly": "#d62728",     # red — treatment
    "llm_unfriendly": "#1f77b4",   # blue — control
}


def setup_style():
    """Call once at the top of a notebook."""
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams["figure.figsize"] = (10, 5)
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.titlesize"] = 12


def add_chatgpt_line(ax, label: str = "ChatGPT release"):
    """Add a vertical line at the treatment date."""
    ax.axvline(TREATMENT_DATE, color="black", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(
        TREATMENT_DATE, ax.get_ylim()[1] * 0.95, f" {label}",
        rotation=90, va="top", ha="left", fontsize=9, alpha=0.7,
    )


def plot_volume_by_tag(panel: pd.DataFrame, log_y: bool = False, ax=None):
    """Spaghetti plot of n_questions over time, one line per tag, colored by group."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 5.5))
    for tag, g in panel.groupby("tag"):
        color = GROUP_COLORS[g["group"].iloc[0]]
        ax.plot(g["month"], g["n_questions"], color=color, alpha=0.6, linewidth=1.2)
    add_chatgpt_line(ax)
    ax.set_xlabel("")
    ax.set_ylabel("Monthly question count" + (" (log)" if log_y else ""))
    if log_y:
        ax.set_yscale("log")
    ax.set_title("Question volume per tag — red: LLM-friendly, blue: LLM-unfriendly")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    return ax


def plot_group_mean(panel: pd.DataFrame, metric: str, ax=None, normalize: bool = False):
    """
    Mean of `metric` per group per month.
    If normalize=True, divide each group by its pre-treatment mean (so both start at 1).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))

    agg = panel.groupby(["month", "group"])[metric].mean().reset_index()

    if normalize:
        pre = panel[panel["post_chatgpt"] == 0].groupby("group")[metric].mean()
        agg["value"] = agg.apply(lambda r: r[metric] / pre[r["group"]], axis=1)
        ycol, ylabel = "value", f"{metric} (normalized to pre-ChatGPT mean = 1)"
    else:
        ycol, ylabel = metric, metric

    for group, g in agg.groupby("group"):
        ax.plot(g["month"], g[ycol], color=GROUP_COLORS[group],
                label=group.replace("_", "-"), linewidth=2)
    add_chatgpt_line(ax)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    ax.legend(loc="best", frameon=True)
    ax.set_title(f"Group mean: {metric}")
    return ax


def plot_pre_post_distribution(panel_or_sample: pd.DataFrame, metric: str,
                               time_col: str = "month", ax=None):
    """Violin/box of metric, pre vs post, split by group."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
    df = panel_or_sample.copy()
    df["period"] = df["post_chatgpt"].map({0: "pre", 1: "post"})
    sns.boxplot(
        data=df, x="period", y=metric, hue="group",
        order=["pre", "post"], palette=GROUP_COLORS, ax=ax,
    )
    ax.set_title(f"{metric}: pre vs post ChatGPT, by group")
    return ax
