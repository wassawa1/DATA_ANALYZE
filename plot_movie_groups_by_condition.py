"""感覚記憶中の高低2群vs正答率_individuals.png と同じ個人ごとデータを使い、
告知・未告知ごとに低/高の正答率を棒グラフで並べて描画。
出力: outputs/感覚記憶_高低_vs_正答率_by_condition.png
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from analysis_utils import (
    load_sheet,
    data_file_path,
    ensure_data_dir,
    save_figure,
    groups,
)

def get_low_high_cols(df):
    low_indices = []
    high_indices = []
    for (s, e, label, color) in groups:
        if '低' in label:
            low_indices.extend(list(range(s, e+1)))
        elif '高' in label:
            high_indices.extend(list(range(s, e+1)))
    low_cols = [f"点数{idx}" for idx in sorted(set(low_indices)) if f"点数{idx}" in df.columns]
    high_cols = [f"点数{idx}" for idx in sorted(set(high_indices)) if f"点数{idx}" in df.columns]
    return low_cols, high_cols


def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")
    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo = load_sheet(data_path, sheet_name="未告知")

    # 低/高列
    low_cols_win, high_cols_win = get_low_high_cols(df_win)
    low_cols_wo, high_cols_wo = get_low_high_cols(df_wo)

    # 各条件ごとに平均正答率
    mean_low_win = df_win[low_cols_win].mean().mean()
    mean_high_win = df_win[high_cols_win].mean().mean()
    mean_low_wo = df_wo[low_cols_wo].mean().mean()
    mean_high_wo = df_wo[high_cols_wo].mean().mean()

    # 棒グラフ用データ
    x = np.arange(2)  # 0:低, 1:高
    width = 0.35

    fig, ax = plt.subplots(figsize=(6, 6))
    bars1 = ax.bar(x - width/2, [mean_low_win, mean_high_win], width=width, color='C0', label='告知')
    bars2 = ax.bar(x + width/2, [mean_low_wo, mean_high_wo], width=width, color='C1', label='未告知')

    # 注記
    for i, bar in enumerate(bars1):
        val = bar.get_height()
        ax.annotate(f"{val*100:.1f}%", xy=(bar.get_x()+bar.get_width()/2, val), xytext=(0,4), textcoords='offset points', ha='center', va='bottom', fontsize=10)
    for i, bar in enumerate(bars2):
        val = bar.get_height()
        ax.annotate(f"{val*100:.1f}%", xy=(bar.get_x()+bar.get_width()/2, val), xytext=(0,4), textcoords='offset points', ha='center', va='bottom', fontsize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(['低', '高'])
    ax.set_ylabel('正答率')
    ax.set_ylim(0, 1.0)
    ax.set_title('感覚記憶：高低 vs 正答率（告知・未告知別）')
    ax.legend()

    fig.tight_layout()
    save_figure(fig, '感覚記憶_高低_vs_正答率_by_condition.png', figsize=fig.get_size_inches())
    plt.close(fig)

if __name__ == '__main__':
    main()