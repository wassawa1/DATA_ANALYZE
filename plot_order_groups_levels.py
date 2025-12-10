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
    if '男' in s:
        return '男性'
    if '女' in s:
        return '女性'
    return None


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

    # normalize gender column to avoid fragmentation
    gender_col = find_gender_column(combined)
    if gender_col is None:
        raise RuntimeError("データに性別を示す列が見つかりませんでした。列名を確認してください。")
    gender_series = combined[gender_col].apply(normalize_gender)
    gender_series.name = '__gender_norm'
    combined = pd.concat([combined, gender_series], axis=1)

    # stats per level and per gender
    level_defs = [
        ("低", same_low, diff_low),
        ("高", same_high, diff_high),
        ("高低", same_highlow, diff_highlow),
    ]

    genders = ['男性', '女性']
    results = {g: [] for g in genders}

    # compute combined (same+diff) per level per gender
    for lvl_name, same_idx, diff_idx in level_defs:
        for g in genders:
            sub = combined[combined['__gender_norm'] == g]
            same_stats = compute_group_stats(sub, same_idx)
            diff_stats = compute_group_stats(sub, diff_idx)
            total_correct = int(same_stats[1]) + int(diff_stats[1])
            total_count = int(same_stats[2]) + int(diff_stats[2])
            mean = (total_correct / total_count) if total_count else 0.0
            results[g].append((mean, total_correct, total_count))

    # plotting grouped bars
    levels = [ld[0] for ld in level_defs]
    x = np.arange(len(levels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 6))
    offsets = [-width/2, width/2]
    colors = ['C0', 'C1']

    for i, g in enumerate(genders):
        stats = results[g]
        vals = [s[0] for s in stats]
        bar_pos = x + offsets[i]
        bars = ax.bar(bar_pos, vals, width=width, color=colors[i], label=g)
        label_fs = max(7, ANNOTATION_FONT_SIZE - 2)
        for bar, s in zip(bars, stats):
            ax.annotate(f"{s[0]*100:.1f}% ({s[1]}/{s[2]})", xy=(bar.get_x()+bar.get_width()/2, bar.get_height()), xytext=(0,6), textcoords='offset points', ha='center', va='bottom', fontsize=label_fs, bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.85, ec='none'))

    ax.set_xticks(x)
    ax.set_xticklabels(levels, fontsize=max(10, ANNOTATION_FONT_SIZE))
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('正答率')
    ax.set_title('順序記憶：レベル別（低 / 高 / 高低） 性別別（合成: 同一+異なる）')
    ax.legend(title='性別')

    # overall mean (both genders combined)
    total_correct = sum([s[1] for g in genders for s in results[g]])
    total_count = sum([s[2] for g in genders for s in results[g]])
    overall_mean = (total_correct / total_count) if total_count else 0.0
    ax.hlines(overall_mean, -0.5, len(levels)-0.5, colors='k', linestyles='--', linewidth=2)
    ax.annotate(f"平均 {overall_mean*100:.1f}%", xy=(len(levels)-0.5, overall_mean), xytext=(6, 6), textcoords='offset points', ha='left', va='bottom', fontsize=max(7, ANNOTATION_FONT_SIZE-2), bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.9, ec='none'))

    save_figure(fig, "順序記憶_levels.png", figsize=fig.get_size_inches())
    plt.close(fig)


if __name__ == "__main__":
    main()
