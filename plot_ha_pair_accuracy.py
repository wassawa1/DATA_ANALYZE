"""HAレベルごとに、指定した設問ペアの左(低) / 右(高) の正答率を比較する棒グラフをペアごとに出力するスクリプト。

出力例: outputs/HA_pair_6_vs_31_外套の色_vs_31.png
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
    LOW_HIGH_PAIRS,
)
from plot_level_by_score import add_group_accuracy_columns
from matplotlib import gridspec


def cols_for_indices(indices):
    return [f"点数{idx}" for idx in indices]


def compute_stats_by_level(df, level_col, cols):
    # cols: list of 点数... columns (may include multiple); compute per-participant mean across cols
    cols_exist = [c for c in cols if c in df.columns]
    if not cols_exist:
        return pd.Series(dtype=float), pd.Series(dtype=int), pd.Series(dtype=int)
    # per-person mean (for averaging across persons)
    per_person = df[cols_exist].mean(axis=1)
    # per-person correct counts and available counts (handle missing)
    per_person_correct = df[cols_exist].fillna(0).astype(float).sum(axis=1)
    per_person_total = df[cols_exist].notna().sum(axis=1)

    grouped_mean = df.assign(_p=per_person).groupby(level_col)['_p']
    mean_by_level = grouped_mean.mean()

    grouped_corr = df.assign(_corr=per_person_correct).groupby(level_col)['_corr']
    grouped_den = df.assign(_den=per_person_total).groupby(level_col)['_den']

    correct_by_level = grouped_corr.sum()
    total_by_level = grouped_den.sum()

    return mean_by_level, correct_by_level, total_by_level


def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")
    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo = load_sheet(data_path, sheet_name="未告知")

    # combine conditions unless user wants separate (currently combined)
    df = pd.concat([df_win, df_wo], ignore_index=True)

    level_col = 'HAレベル'
    levels = sorted(df[level_col].dropna().unique())

    out_dir = os.path.join(os.getcwd(), 'outputs')
    os.makedirs(out_dir, exist_ok=True)

    # aggregate all left indices and all right indices across LOW_HIGH_PAIRS
    left_all = []
    right_all = []
    for l, r in LOW_HIGH_PAIRS:
        left_all.extend(l if isinstance(l, list) else [l])
        right_all.extend(r if isinstance(r, list) else [r])

    left_cols = cols_for_indices(sorted(set(left_all)))
    right_cols = cols_for_indices(sorted(set(right_all)))

    # prepare aggregated stats for top subplot (低 vs 高)
    left_mean, left_corr, left_den = compute_stats_by_level(df, level_col, left_cols)
    right_mean, right_corr, right_den = compute_stats_by_level(df, level_col, right_cols)

    # align levels
    left_mean = left_mean.reindex(levels, fill_value=np.nan)
    right_mean = right_mean.reindex(levels, fill_value=np.nan)
    left_corr = left_corr.reindex(levels, fill_value=0)
    left_den = left_den.reindex(levels, fill_value=0)
    right_corr = right_corr.reindex(levels, fill_value=0)
    right_den = right_den.reindex(levels, fill_value=0)

    # prepare acc columns for VF-level plot (use existing helper)
    df_win = add_group_accuracy_columns(df_win, groups)
    df_wo  = add_group_accuracy_columns(df_wo, groups)

    # Create a single figure with top: aggregated low/high bars, bottom: VFレベル vs 正答率 (bar plot)
    fig = plt.figure(figsize=(14, 12))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.4)

    # Top large axis (subplot 211)
    ax_top = fig.add_subplot(gs[0, 0])
    x = np.arange(len(levels))
    width = 0.35
    bars_l = ax_top.bar(x - width / 2, left_mean.values, width, label='低', color='C0')
    bars_r = ax_top.bar(x + width / 2, right_mean.values, width, label='高', color='C1')
    ax_top.set_xticks(x)
    ax_top.set_xticklabels([str(int(l)) for l in levels], rotation=30, ha='right')
    ax_top.set_ylim(0, 1)
    ax_top.set_ylabel('正答率')
    ax_top.set_xlabel(level_col)
    ax_top.set_title("HAレベル別 正答率：低 vs 高")
    ax_top.legend()
    ann_fs = max(7, ANNOTATION_FONT_SIZE - 2)
    for i, bar in enumerate(bars_l):
        mean = left_mean.values[i]
        h = bar.get_height()
        if not np.isnan(mean):
            corr = int(left_corr.values[i])
            den = int(left_den.values[i])
            ax_top.annotate(f"{mean*100:.1f}%\n({corr}/{den})", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 4),
                            textcoords='offset points', ha='center', va='bottom', fontsize=ann_fs)
    for i, bar in enumerate(bars_r):
        mean = right_mean.values[i]
        h = bar.get_height()
        if not np.isnan(mean):
            corr = int(right_corr.values[i])
            den = int(right_den.values[i])
            ax_top.annotate(f"{mean*100:.1f}%\n({corr}/{den})", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 4),
                            textcoords='offset points', ha='center', va='bottom', fontsize=ann_fs)

    # Bottom axis (subplot 212): VFレベルを x 軸にした低 vs 高 の棒グラフ
    ax_bottom = fig.add_subplot(gs[1, 0])

    # compute low/high stats by VFレベル
    vf_left_mean, vf_left_corr, vf_left_den = compute_stats_by_level(df, 'VFレベル', left_cols)
    vf_right_mean, vf_right_corr, vf_right_den = compute_stats_by_level(df, 'VFレベル', right_cols)

    vf_levels = sorted(set(vf_left_mean.index.tolist()) | set(vf_right_mean.index.tolist()))
    vf_left_mean = vf_left_mean.reindex(vf_levels, fill_value=np.nan)
    vf_right_mean = vf_right_mean.reindex(vf_levels, fill_value=np.nan)
    vf_left_corr = vf_left_corr.reindex(vf_levels, fill_value=0)
    vf_left_den = vf_left_den.reindex(vf_levels, fill_value=0)
    vf_right_corr = vf_right_corr.reindex(vf_levels, fill_value=0)
    vf_right_den = vf_right_den.reindex(vf_levels, fill_value=0)

    x_v = np.arange(len(vf_levels))
    w = 0.35
    bars_lv = ax_bottom.bar(x_v - w/2, vf_left_mean.values, w, label='低', color='C0')
    bars_rv = ax_bottom.bar(x_v + w/2, vf_right_mean.values, w, label='高', color='C1')
    ax_bottom.set_xticks(x_v)
    ax_bottom.set_xticklabels([str(int(v)) for v in vf_levels], rotation=30, ha='right')
    ax_bottom.set_ylim(0, 1)
    ax_bottom.set_ylabel('正答率')
    ax_bottom.set_xlabel('VFレベル')
    ax_bottom.set_title('VFレベル別 正答率：低 vs 高')
    ax_bottom.legend()

    # annotate
    ann_fs = max(7, ANNOTATION_FONT_SIZE - 2)
    for i, bar in enumerate(bars_lv):
        mean = vf_left_mean.values[i]
        if not np.isnan(mean):
            corr = int(vf_left_corr.values[i])
            den = int(vf_left_den.values[i])
            ax_bottom.annotate(f"{mean*100:.1f}%\n({corr}/{den})", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()), xytext=(0,4),
                               textcoords='offset points', ha='center', va='bottom', fontsize=ann_fs)
    for i, bar in enumerate(bars_rv):
        mean = vf_right_mean.values[i]
        if not np.isnan(mean):
            corr = int(vf_right_corr.values[i])
            den = int(vf_right_den.values[i])
            ax_bottom.annotate(f"{mean*100:.1f}%\n({corr}/{den})", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()), xytext=(0,4),
                               textcoords='offset points', ha='center', va='bottom', fontsize=ann_fs)

    fig.subplots_adjust(bottom=0.12, right=0.80)

    save_name = "HA_pair_and_VFlevels.png"
    save_figure(fig, save_name, figsize=fig.get_size_inches())
    plt.close(fig)


if __name__ == '__main__':
    main()
