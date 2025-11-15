"""Low/High の対になった項目ごとに個人の正答率を比較するプロット

このスクリプトは `analyze_v3.py` の内容を整理して作成しました。
"""
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from analysis_utils import load_sheet, data_file_path, output_file_path, ensure_data_dir, ANNOTATION_FONT_SIZE, LEGEND_FONT_SIZE


# Low / High の対応表（ペアリスト）
pairs = [
    (6, 31), (7, 30), (19, 21), (20, 34), (39, 77), (40, 66),
    (44, 92), (45, 69), (49, 79), (52, 84),
    ([53,54,55], [71,72,73,74,75,76]),
    (56, 63), (93, 128), (95, 127), (97, 121), (99, 134),
    (106, 124), (108, 131), (110, 132), (118, 123), (103, 125), (113, 130)
]


def expand_pairs(pairs):
    low_items = []
    high_items = []
    for low, high in pairs:
        low_items.extend(low if isinstance(low, list) else [low])
        high_items.extend(high if isinstance(high, list) else [high])
    return sorted(low_items), sorted(high_items)


def compute_low_high(df, low_items, high_items):
    low_cols  = [f"点数{x}" for x in low_items]
    high_cols = [f"点数{x}" for x in high_items]

    # Compute the two new series without inserting them one-by-one into `df`.
    acc_low = df[low_cols].mean(axis=1)
    acc_high = df[high_cols].mean(axis=1)

    # Attach both columns at once to avoid fragmentation (many small inserts).
    new_cols = pd.concat([acc_low, acc_high], axis=1)
    new_cols.columns = ["acc_low", "acc_high"]
    df = pd.concat([df, new_cols], axis=1)
    return df


def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")
    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo  = load_sheet(data_path, sheet_name="未告知")

    low_items, high_items = expand_pairs(pairs)

    df_win = compute_low_high(df_win, low_items, high_items)
    df_wo  = compute_low_high(df_wo,  low_items, high_items)

    labels = ["Low（低）", "High（高）"]
    x = [0, 1]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=True)

    # 告知（色分け、凡例に氏名）
    lines_win = []
    names_win = []
    cmap = plt.get_cmap("tab20")
    for i, row in df_win.iterrows():
        name = row.get("姓名（漢字）", f"# {i}")
        color = cmap(i % cmap.N)
        line, = ax1.plot(x, [row["acc_low"], row["acc_high"]], color=color, alpha=0.9, label=name)
        lines_win.append(line)
        names_win.append(name)

    ax1.plot(x, [df_win["acc_low"].mean(), df_win["acc_high"].mean()], color="black", linestyle="--", linewidth=3, label="平均")
    ax1.set_title("告知：低群 vs 高群 正答率（個人ごと）")
    ax1.set_ylabel("正答率")
    ax1.set_ylim(0, 1)
    ax1.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=LEGEND_FONT_SIZE)

    cursor1 = mplcursors.cursor(lines_win, hover=True)

    @cursor1.connect("add")
    def on_hover_win(sel):
        idx = lines_win.index(sel.artist)
        name = names_win[idx]
        y_low  = df_win.loc[idx, "acc_low"]
        y_high = df_win.loc[idx, "acc_high"]
        sel.annotation.set(text=f"{name}\nLow: {y_low:.3f}\nHigh: {y_high:.3f}", fontsize=ANNOTATION_FONT_SIZE, bbox=dict(boxstyle="round", fc="white", ec="gray"))

    # 未告知（色分け、凡例に氏名）
    lines_wo = []
    names_wo = []
    cmap = plt.get_cmap("tab20")
    for i, row in df_wo.iterrows():
        name = row.get("姓名（漢字）", f"# {i}")
        color = cmap(i % cmap.N)
        line, = ax2.plot(x, [row["acc_low"], row["acc_high"]], color=color, alpha=0.9, label=name)
        lines_wo.append(line)
        names_wo.append(name)

    ax2.plot(x, [df_wo["acc_low"].mean(), df_wo["acc_high"].mean()], color="black", linestyle="--", linewidth=3, label="平均")
    ax2.set_title("未告知：低群 vs 高群 正答率（個人ごと）")
    ax2.set_ylabel("正答率")
    ax2.set_ylim(0, 1)
    # Do not show duplicate legend for the lower subplot (too many items)

    cursor2 = mplcursors.cursor(lines_wo, hover=True)

    @cursor2.connect("add")
    def on_hover_wo(sel):
        idx = lines_wo.index(sel.artist)
        name = names_wo[idx]
        y_low  = df_wo.loc[idx, "acc_low"]
        y_high = df_wo.loc[idx, "acc_high"]
        sel.annotation.set(text=f"{name}\nLow: {y_low:.3f}\nHigh: {y_high:.3f}", fontsize=ANNOTATION_FONT_SIZE, bbox=dict(boxstyle="round", fc="white", ec="gray"))

    # rotate x labels to match style of other plots and avoid clipping
    plt.xticks(x, labels, rotation=30, ha='right', rotation_mode='anchor')
    # increase bottom margin to make room for rotated labels
    fig.subplots_adjust(bottom=0.30)
    plt.tight_layout()
    out = output_file_path("感覚記憶中の高低2群vs正答率_individuals.png")
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
