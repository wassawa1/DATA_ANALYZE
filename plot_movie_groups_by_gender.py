"""性別ごとに感覚記憶の低/高で正答率を算出し、左右並列の棒グラフを出力するスクリプト。

出力: outputs/感覚記憶_高低_by_gender.png
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


def find_gender_column(df: pd.DataFrame):
    candidates = [c for c in df.columns if '性' in c or 'gender' in c.lower()]
    return candidates[0] if candidates else None


def normalize_gender(val: object):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s in ('男性', '男', 'M', 'm'):
        return '男性'
    if s in ('女性', '女', 'F', 'f'):
        return '女性'
    # fallback: try contains
    if '男' in s:
        return '男性'
    if '女' in s:
        return '女性'
    return None


def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")
    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo = load_sheet(data_path, sheet_name="未告知")

    df = pd.concat([df_win, df_wo], ignore_index=True)

    gender_col = find_gender_column(df)
    if gender_col is None:
        raise RuntimeError("データに性別を示す列が見つかりませんでした（例: '性別'）。列名を確認してください。")

    # avoid DataFrame fragmentation by creating a new Series and concat once
    gender_series = df[gender_col].apply(normalize_gender)
    gender_series.name = '__gender_norm'
    df = pd.concat([df, gender_series], axis=1)

    # determine low/high columns from groups
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

    # prepare grouped bars: for each strength (低, 高) draw 男性 and 女性 bars adjacent
    genders = ['男性', '女性']
    # collect metrics per gender
    results = {}
    y_max = 0
    for g in genders:
        sub = df[df['__gender_norm'] == g]
        if sub.empty:
            mean_low = np.nan
            mean_high = np.nan
            corr_low = den_low = corr_high = den_high = 0
        else:
            per_low = sub[low_cols].mean(axis=1)
            per_high = sub[high_cols].mean(axis=1)
            mean_low = per_low.mean()
            mean_high = per_high.mean()
            corr_low = sub[low_cols].fillna(0).astype(float).sum().sum()
            den_low = sub[low_cols].notna().sum().sum()
            corr_high = sub[high_cols].fillna(0).astype(float).sum().sum()
            den_high = sub[high_cols].notna().sum().sum()

        results[g] = dict(mean_low=mean_low, mean_high=mean_high, corr_low=corr_low, den_low=den_low, corr_high=corr_high, den_high=den_high)
        y_max = max(y_max, 0 if np.isnan(mean_low) else mean_low, 0 if np.isnan(mean_high) else mean_high)

    # plotting grouped bars
    fig, ax = plt.subplots(figsize=(6, 5))
    x = np.arange(2)  # 0: 低, 1: 高
    n_genders = 2
    width = 0.35
    offsets = np.linspace(-width/2, width/2, n_genders)

    colors = ['C0', 'C1']
    labels = ['男性', '女性']

    for i, g in enumerate(genders):
        r = results[g]
        vals = [r['mean_low'] if not np.isnan(r['mean_low']) else 0, r['mean_high'] if not np.isnan(r['mean_high']) else 0]
        bar_pos = x + offsets[i]
        bars = ax.bar(bar_pos, vals, width=width, color=colors[i], label=labels[i])
        ann_fs = max(8, ANNOTATION_FONT_SIZE)
        # annotate each bar
        for j, b in enumerate(bars):
            if j == 0:
                den = r['den_low']
                corr = r['corr_low']
                val = r['mean_low']
            else:
                den = r['den_high']
                corr = r['corr_high']
                val = r['mean_high']

            if den > 0 and not np.isnan(val):
                ax.annotate(f"{(val*100):.1f}%\n({int(corr)}/{int(den)})", xy=(b.get_x()+b.get_width()/2, b.get_height()), xytext=(0,4), textcoords='offset points', ha='center', va='bottom', fontsize=ann_fs)
            else:
                ax.annotate("N/A", xy=(b.get_x()+b.get_width()/2, b.get_height()), xytext=(0,4), textcoords='offset points', ha='center', va='bottom', fontsize=ann_fs)

    ax.set_xticks(x)
    ax.set_xticklabels(['低', '高'])
    ax.set_ylabel('正答率')
    # ensure Y axis goes to 1.0 for consistency with other plots
    ax.set_ylim(0, 1.0)
    ax.set_title('感覚記憶：強度(低/高) vs 正答率（性別別、告知/未告知 合算）')
    ax.legend(title='性別')

    save_name = '感覚記憶_高低_by_gender.png'
    save_figure(fig, save_name, figsize=fig.get_size_inches())
    plt.close(fig)


if __name__ == '__main__':
    main()
