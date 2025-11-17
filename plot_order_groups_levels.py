"""順序記憶の設問群をレベル別に (低 / 高 / 高低) 集約し、
各レベルで「同一」vs「異なる」を比較する棒グラフを作成します。

出力: `outputs/順序記憶_levels.png`
"""
import numpy as np
import matplotlib.pyplot as plt

from analysis_utils import (
    load_sheet,
    data_file_path,
    ensure_data_dir,
    save_figure,
    ANNOTATION_FONT_SIZE,
)

import pandas as pd


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

    # レベルごとのインデックス定義
    same_high = list(range(135, 141)) + list(range(171, 177))
    diff_high = list(range(153, 159)) + list(range(189, 195))

    same_low = list(range(141, 147)) + list(range(177, 183))
    diff_low = list(range(159, 165)) + list(range(195, 201))

    same_highlow = list(range(147, 153)) + list(range(183, 189))
    diff_highlow = list(range(165, 171)) + list(range(201, 207))

    # 合成データ (告知+未告知)
    combined = pd.concat([df_win, df_wo], ignore_index=True)

    same_high_stats = compute_group_stats(combined, same_high)
    diff_high_stats = compute_group_stats(combined, diff_high)

    same_low_stats = compute_group_stats(combined, same_low)
    diff_low_stats = compute_group_stats(combined, diff_low)

    same_hl_stats = compute_group_stats(combined, same_highlow)
    diff_hl_stats = compute_group_stats(combined, diff_highlow)

    levels = ["低", "高", "高低"]
    same_means = [same_low_stats[0], same_high_stats[0], same_hl_stats[0]]
    diff_means = [diff_low_stats[0], diff_high_stats[0], diff_hl_stats[0]]

    x = np.arange(len(levels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 6))

    # Combine same and diff for each level into a single bar (weighted mean)
    combined_stats_per_level = []
    for same_s, diff_s in zip([same_low_stats, same_high_stats, same_hl_stats],
                              [diff_low_stats, diff_high_stats, diff_hl_stats]):
        total_correct = int(same_s[1]) + int(diff_s[1])
        total_count = int(same_s[2]) + int(diff_s[2])
        mean = (total_correct / total_count) if total_count else 0
        combined_stats_per_level.append((mean, total_correct, total_count))

    combined_means = [s[0] for s in combined_stats_per_level]

    bars = ax.bar(x, combined_means, width*1.0, color='C2')

    ax.set_xticks(x)
    ax.set_xticklabels(levels, fontsize=max(10, ANNOTATION_FONT_SIZE))
    ax.set_ylim(0, 1)
    ax.set_ylabel('正答率')
    ax.set_title('順序記憶：レベル別（低 / 高 / 高低） 合成（同一+異なる）')

    fig.subplots_adjust(bottom=0.20, right=0.78)

    def fmt(mean, n, d):
        return f"{mean*100:.1f}% ({n}/{d})"

    label_fs = max(7, ANNOTATION_FONT_SIZE - 2)
    for bar, stats in zip(bars, combined_stats_per_level):
        h = bar.get_height()
        ax.annotate(fmt(*stats), xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 6),
                    textcoords='offset points', ha='center', va='bottom', fontsize=label_fs,
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.85, ec='none'))

    # 全体平均ライン（同一+異なる 全体）
    total_correct = sum([same_low_stats[1], diff_low_stats[1], same_high_stats[1], diff_high_stats[1], same_hl_stats[1], diff_hl_stats[1]])
    total_count = sum([same_low_stats[2], diff_low_stats[2], same_high_stats[2], diff_high_stats[2], same_hl_stats[2], diff_hl_stats[2]])
    overall_mean = (total_correct / total_count) if total_count else 0
    ax.hlines(overall_mean, -0.5, len(levels)-0.5, colors='k', linestyles='--', linewidth=2)
    ax.annotate(f"平均 {overall_mean*100:.1f}%", xy=(len(levels)-0.5, overall_mean), xytext=(6, 6),
                textcoords='offset points', ha='left', va='bottom', fontsize=max(7, ANNOTATION_FONT_SIZE-2),
                bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.9, ec='none'))

    save_figure(fig, "順序記憶_levels.png", figsize=fig.get_size_inches())
    plt.show()


if __name__ == "__main__":
    main()
