"""色判断設問の正答率（感覚記憶-色 vs 順序記憶）の比較棒グラフ

感覚記憶側はユーザー指定の色判断設問番号集合（点数列の番号）を用いる。
順序記憶側は点数135-206の全体を使用し、`plot_memory_type_accuracy.py` と同じ扱いにする。

出力: `outputs/色判断_vs_順序_memory_type_accuracy.png`
"""
import numpy as np
import matplotlib.pyplot as plt

from analysis_utils import (
    load_sheet,
    data_file_path,
    ensure_data_dir,
    save_figure,
    LEGEND_FONT_SIZE,
    ANNOTATION_FONT_SIZE,
)


def compute_group_mean_accuracy(df, cols):
    """指定した点数列群に対するデータフレーム全体の平均正答率と合計正解数・合計件数を返す。

    戻り値: (mean_float, total_correct, total_count)
    """
    cols_exist = [c for c in cols if c in df.columns]
    if len(cols_exist) == 0:
        raise ValueError("指定した点数列が見つかりませんでした: %s" % cols[:5])

    per_person = df[cols_exist].mean(axis=1)
    mean_val = per_person.mean()

    total_correct = df[cols_exist].sum().sum()
    total_count = df[cols_exist].notna().sum().sum()

    return mean_val, int(total_correct), int(total_count)


def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")

    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo = load_sheet(data_path, sheet_name="未告知")

    # ユーザー指定の色判断設問番号（点数列の番号）
    clothing = [3, 6, 12, 31, 48, 51, 58, 67, 68, 78, 81, 85, 86, 87, 88, 91, 93, 97, 105, 108, 109, 110, 113, 116, 121, 122, 126, 128, 130, 131, 132]
    accessory = [82, 101]
    objects = [7, 11, 17, 18, 25, 30, 33, 39, 57, 60, 62, 77, 114, 117, 118, 119, 123, 129, 133]
    face = [1, 22, 23, 35, 42, 43, 45, 64, 69, 94, 96, 120]
    signage = [10, 16, 52, 59, 61, 84]

    # すべての色判断設問を統合（重複防止のため set を使う）
    color_items = sorted(set(clothing + accessory + objects + face + signage))

    sensory_cols = [f"点数{i}" for i in color_items]
    order_cols = [f"点数{i}" for i in range(135, 207)]

    win_sensory, win_sensory_n, win_sensory_d = compute_group_mean_accuracy(df_win, sensory_cols)
    win_order, win_order_n, win_order_d = compute_group_mean_accuracy(df_win, order_cols)

    wo_sensory, wo_sensory_n, wo_sensory_d = compute_group_mean_accuracy(df_wo, sensory_cols)
    wo_order, wo_order_n, wo_order_d = compute_group_mean_accuracy(df_wo, order_cols)

    groups = ["感覚記憶-色", "順序記憶"]
    x = np.arange(len(groups))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))

    bars1 = ax.bar(x - width / 2, [win_sensory, win_order], width, label="告知", color="C0")
    bars2 = ax.bar(x + width / 2, [wo_sensory, wo_order], width, label="未告知", color="C1")

    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=30, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("正答率")
    ax.set_title("色判断（感覚記憶） vs 順序記憶：告知/未告知 の平均正答率")

    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=LEGEND_FONT_SIZE)
    fig.subplots_adjust(bottom=0.25, right=0.78)

    labels = [
        (win_sensory, win_sensory_n, win_sensory_d),
        (win_order, win_order_n, win_order_d),
    ]
    labels2 = [
        (wo_sensory, wo_sensory_n, wo_sensory_d),
        (wo_order, wo_order_n, wo_order_d),
    ]

    def format_label(mean, n, d):
        pct = mean * 100
        return f"{pct:.1f}% ({n}/{d})"

    for bar, lab in zip(bars1, labels):
        h = bar.get_height()
        ax.annotate(format_label(*lab), xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 6),
                    textcoords='offset points', ha='center', va='bottom', fontsize=max(6, ANNOTATION_FONT_SIZE-2))

    for bar, lab in zip(bars2, labels2):
        h = bar.get_height()
        ax.annotate(format_label(*lab), xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 6),
                    textcoords='offset points', ha='center', va='bottom', fontsize=max(6, ANNOTATION_FONT_SIZE-2))

    save_figure(fig, "色判断_vs_順序_memory_type_accuracy.png", figsize=fig.get_size_inches())
    plt.show()


if __name__ == "__main__":
    main()
