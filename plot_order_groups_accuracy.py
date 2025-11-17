"""順序記憶 (135-206) を 6 グループに分けて、告知/未告知 の正答率を描画するスクリプト

グループ定義:
* 同一動画(高)：135-140 + 171-176
* 同一動画(低)：141-146 + 177-182
* 同一作品(高低)：147-152 + 183-188
* 異なる動画(高)：153-158 + 189-194
* 異なる動画(低)：159-164 + 195-200
* 異なる作品(高低)：165-170 + 201-206

出力: `outputs/順序記憶_6groups_accuracy.png`
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import matplotlib.image as mpimg

from analysis_utils import (
    load_sheet,
    data_file_path,
    ensure_data_dir,
    save_figure,
    ANNOTATION_FONT_SIZE,
    OUTPUT_DPI,
    LEGEND_FONT_SIZE,
)


def compute_group_stats(df, indices):
    """指定インデックスリスト（点数番号）に対して平均正答率と合計正解・合計件数を返す。

    indices: iterable of ints (例: [135,136,...])
    戻り値: (mean, total_correct, total_count)
    """
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

    groups = [
        (list(range(135, 141)) + list(range(171, 177)), "同一動画(高)"),
        (list(range(141, 147)) + list(range(177, 183)), "同一動画(低)"),
        (list(range(147, 153)) + list(range(183, 189)), "同一作品(高低)"),
        (list(range(153, 159)) + list(range(189, 195)), "異なる動画(高)"),
        (list(range(159, 165)) + list(range(195, 201)), "異なる動画(低)"),
        (list(range(165, 171)) + list(range(201, 207)), "異なる作品(高低)"),
    ]

    names = [g[1] for g in groups]

    win_stats = [compute_group_stats(df_win, g[0]) for g in groups]
    wo_stats = [compute_group_stats(df_wo, g[0]) for g in groups]

    win_means = [s[0] for s in win_stats]
    wo_means = [s[0] for s in wo_stats]

    x = np.arange(len(groups))
    width = 0.35

    # Try to match the pixel size of an existing reference image if present
    ref_name = '感覚記憶中の強度vs正答率_movie_groups.png'
    ref_path = os.path.join(os.getcwd(), 'outputs', ref_name)
    if os.path.exists(ref_path):
        try:
            img = mpimg.imread(ref_path)
            h, w = img.shape[0], img.shape[1]
            figsize = (w / OUTPUT_DPI, h / OUTPUT_DPI)
        except Exception:
            figsize = (12, 8)
    else:
        figsize = (12, 8)

    fig, ax = plt.subplots(1, 1, figsize=figsize)

    # grouped bars: 告知 (win) left, 未告知 (wo) right
    bars_win = ax.bar(x - width/2, win_means, width, label='告知', color='C0')
    bars_wo = ax.bar(x + width/2, wo_means, width, label='未告知', color='C1')

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=30, ha='right')
    ax.set_ylim(0, 1)
    ax.set_ylabel('正答率')
    ax.set_title('順序記憶 6 グループ別：告知／未告知 の平均正答率')

    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=LEGEND_FONT_SIZE)
    fig.subplots_adjust(bottom=0.30, right=0.78)

    def format_label(mean, n, d):
        return f"{mean*100:.1f}% ({n}/{d})"

    # annotate
    for bar, stats in zip(bars_win, win_stats):
        h = bar.get_height()
        ax.annotate(format_label(*stats), xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 6),
                    textcoords='offset points', ha='center', va='bottom', fontsize=max(6, ANNOTATION_FONT_SIZE-2))

    for bar, stats in zip(bars_wo, wo_stats):
        h = bar.get_height()
        ax.annotate(format_label(*stats), xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 6),
                    textcoords='offset points', ha='center', va='bottom', fontsize=max(6, ANNOTATION_FONT_SIZE-2))

    save_figure(fig, "順序記憶_6groups_告知未告知.png", figsize=fig.get_size_inches())

    # --- 合成グラフ: 告知/未告知 を分けずに 6 グループの平均を描画 ---
    combined_df = pd.concat([df_win, df_wo], ignore_index=True)
    combined_stats = [compute_group_stats(combined_df, g[0]) for g in groups]
    combined_means = [s[0] for s in combined_stats]

    fig2, ax2 = plt.subplots(1, 1, figsize=figsize)
    bars_comb = ax2.bar(x, combined_means, width*2, color='C2')
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=30, ha='right')
    # 上側に余白を作って注釈や平均線が重ならないようにする
    top_limit = min(1.12, max(1.0, max(combined_means) + 0.12))
    ax2.set_ylim(0, top_limit)
    ax2.set_ylabel('正答率')
    ax2.set_title('順序記憶 6 グループ別：告知/未告知 合成平均')

    # バーラベルを大きめに、白背景ボックスで見やすく配置
    label_fs = max(8, ANNOTATION_FONT_SIZE + 4)
    for bar, stats in zip(bars_comb, combined_stats):
        h = bar.get_height()
        ax2.annotate(
            format_label(*stats),
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 6),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=label_fs,
            bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.85, ec='none')
        )

    # 全体平均（合計正解 / 合計件数）を計算して黒の点線で描画
    total_correct = sum(s[1] for s in combined_stats)
    total_count = sum(s[2] for s in combined_stats)
    overall_mean = (total_correct / total_count) if total_count else 0
    ax2.hlines(overall_mean, -0.5, len(groups) - 0.5, colors='k', linestyles='--', linewidth=3)
    # 平均ラベルは線の右側に表示して重なりを回避
    mean_label_fs = max(9, ANNOTATION_FONT_SIZE + 3)
    ax2.annotate(
        f"平均 {overall_mean*100:.1f}%",
        xy=(len(groups) - 0.5, overall_mean),
        xytext=(10, 6),
        textcoords='offset points',
        ha='left',
        va='bottom',
        fontsize=mean_label_fs,
        bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.9, ec='none')
    )

    fig2.subplots_adjust(top=0.92)
    save_figure(fig2, "順序記憶_6groups.png", figsize=fig2.get_size_inches())
    plt.show()


if __name__ == "__main__":
    main()
