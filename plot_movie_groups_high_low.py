"""映画毎の低/高をまとめて、感覚記憶中の強度(低/高) vs 正答率 を出力するスクリプト。

出力: outputs/感覚記憶_高低_vs_正答率.png
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from analysis_utils import (
    load_sheet,
    data_file_path,
    ensure_data_dir,
    save_figure,
    ANNOTATION_FONT_SIZE,
    groups,
)


def cols_for_range(start, end):
    # start/end inclusive
    return [f"点数{idx}" for idx in range(start, end+1)]


def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")
    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo = load_sheet(data_path, sheet_name="未告知")

    # combine conditions (告知/未告知 を分けない)
    df = pd.concat([df_win, df_wo], ignore_index=True)

    # Collect low/high item columns from groups
    low_indices = []
    high_indices = []
    for (s, e, label, color) in groups:
        if '低' in label:
            low_indices.extend(list(range(s, e+1)))
        elif '高' in label:
            high_indices.extend(list(range(s, e+1)))

    low_cols = [f"点数{idx}" for idx in sorted(set(low_indices)) if f"点数{idx}" in df.columns]
    high_cols = [f"点数{idx}" for idx in sorted(set(high_indices)) if f"点数{idx}" in df.columns]

    if not low_cols or not high_cols:
        raise RuntimeError("低/高 の点数列が見つかりませんでした。データ列名を確認してください。")

    # per-person means
    per_low = df[low_cols].mean(axis=1)
    per_high = df[high_cols].mean(axis=1)

    # overall means (across participants)
    mean_low = per_low.mean()
    mean_high = per_high.mean()

    # counts for annotations
    corr_low = df[low_cols].fillna(0).astype(float).sum().sum()
    den_low = df[low_cols].notna().sum().sum()
    corr_high = df[high_cols].fillna(0).astype(float).sum().sum()
    den_high = df[high_cols].notna().sum().sum()

    # Plot two bars
    fig, ax = plt.subplots(figsize=(6, 6))
    x = np.arange(2)
    width = 0.6
    bars = ax.bar(x, [mean_low, mean_high], width, color=['C0', 'C1'])
    ax.set_xticks(x)
    ax.set_xticklabels(['低', '高'])
    ax.set_ylim(0, 1)
    ax.set_ylabel('正答率')
    ax.set_title('感覚記憶：強度(低/高) vs 正答率（合算）')

    ann_fs = max(8, ANNOTATION_FONT_SIZE)
    ax.annotate(f"{mean_low*100:.1f}%\n({int(corr_low)}/{int(den_low)})", xy=(bars[0].get_x()+bars[0].get_width()/2, bars[0].get_height()), xytext=(0,4), textcoords='offset points', ha='center', va='bottom', fontsize=ann_fs)
    ax.annotate(f"{mean_high*100:.1f}%\n({int(corr_high)}/{int(den_high)})", xy=(bars[1].get_x()+bars[1].get_width()/2, bars[1].get_height()), xytext=(0,4), textcoords='offset points', ha='center', va='bottom', fontsize=ann_fs)

    save_name = '感覚記憶_高低_vs_正答率.png'
    save_figure(fig, save_name, figsize=fig.get_size_inches())
    plt.close(fig)


if __name__ == '__main__':
    main()
