"""HAレベルごと（高・低）の正答率を棒グラフで描画。
出力: outputs/HA_level_vs_accuracy.png
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from analysis_utils import (
    load_sheet,
    data_file_path,
    ensure_data_dir,
    save_figure,
    LOW_HIGH_PAIRS,
    expand_pairs,
)

def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")
    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo = load_sheet(data_path, sheet_name="未告知")
    df = pd.concat([df_win, df_wo], ignore_index=True)

    # LOW_HIGH_PAIRSからlow/highの設問番号リストを取得
    low_items, high_items = expand_pairs(LOW_HIGH_PAIRS)
    low_cols = [f"点数{idx}" for idx in low_items if f"点数{idx}" in df.columns]
    high_cols = [f"点数{idx}" for idx in high_items if f"点数{idx}" in df.columns]

    # HAレベルごとに正答率を計算
    level_col = 'HAレベル'
    levels = sorted(df[level_col].dropna().unique())
    low_means = []
    high_means = []
    for lvl in levels:
        sub = df[df[level_col] == lvl]
        mean_low = sub[low_cols].mean().mean() if not sub.empty else np.nan
        mean_high = sub[high_cols].mean().mean() if not sub.empty else np.nan
        low_means.append(mean_low)
        high_means.append(mean_high)

    x = np.arange(len(levels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(max(7, len(levels)*0.7), 6))
    bars1 = ax.bar(x - width/2, low_means, width=width, color='C0', label='低')
    bars2 = ax.bar(x + width/2, high_means, width=width, color='C1', label='高')
    ax.set_xticks(x)
    ax.set_xticklabels([str(l) for l in levels])
    ax.set_ylabel('正答率')
    ax.set_ylim(0, 1.0)
    ax.set_title('HAレベルごとの正答率（低・高）')
    ax.legend()

    # 注記
    for i, bar in enumerate(bars1):
        val = bar.get_height()
        ax.annotate(f"{val*100:.1f}%", xy=(bar.get_x()+bar.get_width()/2, val), xytext=(0,4), textcoords='offset points', ha='center', va='bottom', fontsize=10)
    for i, bar in enumerate(bars2):
        val = bar.get_height()
        ax.annotate(f"{val*100:.1f}%", xy=(bar.get_x()+bar.get_width()/2, val), xytext=(0,4), textcoords='offset points', ha='center', va='bottom', fontsize=10)

    fig.tight_layout()
    save_figure(fig, 'HA_level_vs_accuracy.png', figsize=fig.get_size_inches())
    plt.close(fig)

if __name__ == '__main__':
    main()