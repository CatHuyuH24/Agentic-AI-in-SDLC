"""Headless figure export script.

Exports the four canonical charts as static PNG files to ``outputs/figures/``
using matplotlib (no browser or kaleido required).  Run from the project root:

    python scripts/export_figures.py

Output files:
    outputs/figures/prediction_distribution.png
    outputs/figures/confidence_drop.png
    outputs/figures/temporal_leakage_warning.png
    outputs/figures/faithfulness_radar.png
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR  = PROJECT_ROOT / "outputs" / "figures"
RESULTS_CSV  = PROJECT_ROOT / "outputs" / "faithfulness_results.csv"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

PNG_WIDTH_IN  = 12   # inches
PNG_HEIGHT_IN = 7    # inches
DPI           = 100  # → 1200 x 700 px (≥ 1200 wide)

PALETTE = {
    "UP":   "#22C55E",
    "DOWN": "#EF4444",
    "HOLD": "#94A3B8",
    "blue": "#6366F1",
    "pink": "#EC4899",
    "amber": "#F59E0B",
    "valid": "#22C55E",
    "invalid": "#EF4444",
}


def _save_fig(fig, fname: str) -> None:
    import matplotlib.pyplot as plt
    out = FIGURES_DIR / fname
    fig.savefig(str(out), dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.relative_to(PROJECT_ROOT)}")


def export_prediction_distribution(df) -> None:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("Agg")

    counts = df["prediction"].value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()
    colors = [PALETTE.get(l, PALETTE["blue"]) for l in labels]

    fig, ax = plt.subplots(figsize=(PNG_WIDTH_IN, PNG_HEIGHT_IN))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(val), ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_title("Prediction Distribution Across All Records", fontsize=15, fontweight="bold", pad=16)
    ax.set_xlabel("Predicted Direction", fontsize=12)
    ax.set_ylabel("Number of Records", fontsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor("#F8FAFC")
    fig.patch.set_facecolor("white")
    _save_fig(fig, "prediction_distribution.png")


def export_confidence_drop(df) -> None:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("Agg")

    ticker_order = sorted(df["ticker"].unique())
    avg = df.groupby("ticker")["confidence_drop"].mean()
    vals = [avg.get(t, 0.0) for t in ticker_order]
    colors = [PALETTE["blue"], PALETTE["pink"], PALETTE["amber"]] + [PALETTE["blue"]] * 10

    fig, ax = plt.subplots(figsize=(PNG_WIDTH_IN, PNG_HEIGHT_IN))
    bars = ax.bar(ticker_order, vals, color=colors[:len(ticker_order)], edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{val:.1%}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(vals) * 1.25 if max(vals) > 0 else 1)
    ax.set_title("Average Confidence Drop per Ticker", fontsize=15, fontweight="bold", pad=16)
    ax.set_xlabel("Ticker", fontsize=12)
    ax.set_ylabel("Avg Confidence Drop", fontsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor("#F8FAFC")
    fig.patch.set_facecolor("white")
    _save_fig(fig, "confidence_drop.png")


def export_temporal_leakage(df) -> None:
    import matplotlib.pyplot as plt
    import matplotlib
    import numpy as np
    matplotlib.use("Agg")

    tickers = sorted(df["ticker"].unique())
    valid_counts   = [df[df["ticker"] == t]["valid_news_count"].sum() for t in tickers]
    invalid_counts = [df[df["ticker"] == t]["invalid_future_news_count"].sum() for t in tickers]

    x = np.arange(len(tickers))
    width = 0.35

    fig, ax = plt.subplots(figsize=(PNG_WIDTH_IN, PNG_HEIGHT_IN))
    b1 = ax.bar(x - width / 2, valid_counts,   width, label="Valid News",           color=PALETTE["valid"],   edgecolor="white")
    b2 = ax.bar(x + width / 2, invalid_counts, width, label="Future-Dated (Leaked)", color=PALETTE["invalid"], edgecolor="white")

    for bar in list(b1) + list(b2):
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3,
                    str(int(h)), ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_title("Temporal Leakage Warning: Valid vs Future-Dated News per Ticker",
                 fontsize=13, fontweight="bold", pad=16)
    ax.set_xlabel("Ticker", fontsize=12)
    ax.set_ylabel("News Item Count", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(tickers, fontsize=11)
    ax.legend(fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor("#F8FAFC")
    fig.patch.set_facecolor("white")
    _save_fig(fig, "temporal_leakage_warning.png")


def export_faithfulness_radar(df) -> None:
    import matplotlib.pyplot as plt
    import matplotlib
    import numpy as np
    matplotlib.use("Agg")

    metrics = ["temporal_validity", "evidence_support", "confidence_drop"]
    labels  = ["Temporal\nValidity", "Evidence\nSupport", "Confidence\nDrop"]
    means   = [df[m].mean() for m in metrics]

    N = len(metrics)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    # Close the polygon
    values = means + [means[0]]
    angles += [angles[0]]
    label_angles = angles[:N]

    fig, ax = plt.subplots(figsize=(PNG_HEIGHT_IN, PNG_HEIGHT_IN), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color=PALETTE["blue"], alpha=0.25)
    ax.plot(angles, values, color=PALETTE["blue"], linewidth=2, marker="o", markersize=7)

    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], fontsize=9, color="grey")
    ax.set_ylim(0, 1)
    ax.set_xticks(label_angles)
    ax.set_xticklabels(labels, fontsize=12, fontweight="bold")

    for angle, val, label in zip(label_angles, means, labels):
        ax.text(angle, val + 0.08, f"{val:.2f}", ha="center", va="center",
                fontsize=10, color=PALETTE["blue"], fontweight="bold")

    ax.set_title("Faithfulness Metrics Radar (Corpus Average)",
                 fontsize=13, fontweight="bold", pad=20)
    fig.patch.set_facecolor("white")
    _save_fig(fig, "faithfulness_radar.png")


def main() -> None:
    try:
        import pandas as pd
        import matplotlib
    except ImportError as exc:
        print(f"ERROR: Missing dependency — {exc}. Run: pip install pandas matplotlib")
        sys.exit(1)

    if not RESULTS_CSV.exists():
        print(
            f"ERROR: {RESULTS_CSV} not found.\n"
            "Run `python src/main.py` first to generate faithfulness results."
        )
        sys.exit(1)

    import pandas as pd
    print(f"Loading {RESULTS_CSV.relative_to(PROJECT_ROOT)} ...")
    df = pd.read_csv(RESULTS_CSV)
    print(f"  {len(df)} rows loaded.\n")

    print("Exporting figures to outputs/figures/ ...")
    export_prediction_distribution(df)
    export_confidence_drop(df)
    export_temporal_leakage(df)
    export_faithfulness_radar(df)
    print("\nDone. 4 PNG files written.")


if __name__ == "__main__":
    main()
