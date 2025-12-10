"""HAペアごとに低・高の正答率を棒グラフで描画。
出力: outputs/HA_pair_level_vs_accuracy.png
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
    get_ha_level,
)

def main():
    # --- データ内容をprintで洗い出し ---
    print("--- 使用している設問番号（低グループ）---")
    print([int(col.replace('点数','')) for col in low_cols])
    print("--- 使用している設問番号（高グループ）---")
    print([int(col.replace('点数','')) for col in high_cols])
    print(f"低グループ: 分子={int(n_low)}, 分母={int(d_low)}, 平均={mean_low}")
    print(f"高グループ: 分子={int(n_high)}, 分母={int(d_high)}, 平均={mean_high}")
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")
    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo = load_sheet(data_path, sheet_name="未告知")
    df = pd.concat([df_win, df_wo], ignore_index=True)

    # 横軸: HAレベル(1,2,3,4)、各レベルで低・高の正答率を棒グラフで並べる
    # ペア設問（LOW_HIGH_PAIRS）の左側を低、右側を高として全体平均を集計
    from analysis_utils import LOW_HIGH_PAIRS
    low_indices = []
    high_indices = []
    for low, high in LOW_HIGH_PAIRS:
        if isinstance(low, list):
            low_indices.extend(low)
        else:
            low_indices.append(low)
        if isinstance(high, list):
            high_indices.extend(high)
        else:
            high_indices.append(high)
    low_cols = [f"点数{idx}" for idx in sorted(set(low_indices)) if f"点数{idx}" in df.columns]
    high_cols = [f"点数{idx}" for idx in sorted(set(high_indices)) if f"点数{idx}" in df.columns]

    mean_low = df[low_cols].mean().mean() if low_cols else float('nan')
    mean_high = df[high_cols].mean().mean() if high_cols else float('nan')
    n_low = df[low_cols].fillna(0).astype(float).sum().sum() if low_cols else 0
    d_low = df[low_cols].notna().sum().sum() if low_cols else 0
    n_high = df[high_cols].fillna(0).astype(float).sum().sum() if high_cols else 0
    d_high = df[high_cols].notna().sum().sum() if high_cols else 0

    x = np.arange(2)
    width = 0.5
    fig, ax = plt.subplots(figsize=(6, 6))
    bars = ax.bar(x, [mean_low, mean_high], width=width, color=['C0', 'C1'])
    ax.set_xticks(x)
    ax.set_xticklabels(['低', '高'])
    ax.set_ylabel('正答率', fontsize=13)
    ax.set_ylim(0, 1.0)
    ax.set_title('HAレベルごとの正答率（同タイプ設問ペア）', fontsize=15)
    for i, bar in enumerate(bars):
        if i == 0:
            val = bar.get_height()
            n = int(n_low)
            d = int(d_low)
        else:
            val = bar.get_height()
            n = int(n_high)
            d = int(d_high)
        label = f"{val*100:.1f}%\n({n}/{d})" if d > 0 else "N/A"
        ax.annotate(label, xy=(bar.get_x()+bar.get_width()/2, val), xytext=(0,4), textcoords='offset points', ha='center', va='bottom', fontsize=11)
    fig.tight_layout()
    save_figure(fig, 'HA_level_vs_accuracy.png', figsize=fig.get_size_inches())
    plt.close(fig)

if __name__ == '__main__':
    main()