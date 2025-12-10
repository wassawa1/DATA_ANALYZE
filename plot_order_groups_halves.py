"""順序記憶の 6 グループを前半3グループ / 後半3グループに分けて
告知 / 未告知 の平均正答率を並べた棒グラフを作成するスクリプト。

出力: `outputs/順序記憶_6groups_halves.png`
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
    OUTPUT_DPI,
)


def compute_group_stats(df, indices):
    cols = [f"点数{i}" for i in indices if f"点数{i}" in df.columns]
    if not cols:
        return 0.0, 0, 0
    per_person = df[cols].mean(axis=1)
    mean_val = per_person.mean()
    total_correct = int(df[cols].sum().sum())
    total_count = int(df[cols].notna().sum().sum())
    return mean_val, total_correct, total_count


def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")

    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo = load_sheet(data_path, sheet_name="未告知")

    # グループ定義（そのまま）
    groups = [
        (list(range(135, 141)) + list(range(171, 177)), "同一動画(高)"),
        (list(range(141, 147)) + list(range(177, 183)), "同一動画(低)"),
        (list(range(147, 153)) + list(range(183, 189)), "同一作品(高低)"),
        (list(range(153, 159)) + list(range(189, 195)), "異なる動画(高)"),
        (list(range(159, 165)) + list(range(195, 201)), "異なる動画(低)"),
        (list(range(165, 171)) + list(range(201, 207)), "異なる作品(高低)"),
    ]

    # 前半3つ / 後半3つ のインデックス集合を作成
    first_three = [i for grp in groups[:3] for i in grp[0]]
    last_three = [i for grp in groups[3:] for i in grp[0]]

    # 告知/未告知 を統合して、前半＝「同一」、後半＝「異なる」の2本の棒を作る
    combined_df = pd.concat([df_win, df_wo], ignore_index=True)
    combined_first = compute_group_stats(combined_df, first_three)
    combined_last = compute_group_stats(combined_df, last_three)

    labels = ["同一", "異なる"]
    x = np.arange(len(labels))
    width = 0.6

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(x, [combined_first[0], combined_last[0]], width, color=['C2', 'C3'])

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0, fontsize=max(10, ANNOTATION_FONT_SIZE))
    top_limit = min(1.12, max(1.0, max(combined_first[0], combined_last[0]) + 0.12))
    ax.set_ylim(0, top_limit)
    ax.set_ylabel('正答率')
    ax.set_title('順序記憶：同一（前半3） vs 異なる（後半3） - 合成')

    fig.subplots_adjust(bottom=0.20)

    def fmt(mean, n, d):
        return f"{mean*100:.1f}% ({n}/{d})"

    label_fs = max(10, ANNOTATION_FONT_SIZE + 1)
    for bar, stats in zip(bars, [combined_first, combined_last]):
        h = bar.get_height()
        ax.annotate(
            fmt(*stats),
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 6),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=label_fs,
            bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.85, ec='none')
        )

    overall_correct = combined_first[1] + combined_last[1]
    overall_count = combined_first[2] + combined_last[2]
    overall_mean = (overall_correct / overall_count) if overall_count else 0
    ax.hlines(overall_mean, -0.5, len(labels)-0.5, colors='k', linestyles='--', linewidth=3)
    ax.annotate(f"平均 {overall_mean*100:.1f}%", xy=(len(labels)-0.5, overall_mean), xytext=(10, 6),
                textcoords='offset points', ha='left', va='bottom', fontsize=max(10, ANNOTATION_FONT_SIZE),
                bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.9, ec='none'))

    save_figure(fig, "順序記憶_6groups_halves.png", figsize=fig.get_size_inches())
    plt.show()


if __name__ == "__main__":
    import pandas as pd
    main()
