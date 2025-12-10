"""HA/VF レベルごとの平均正答率を描画するスクリプト（告知/未告知の2段プロット）
"""
import pandas as pd
import matplotlib.pyplot as plt
from analysis_utils import load_sheet, groups, data_file_path, output_file_path, ensure_data_dir, LEGEND_FONT_SIZE


def add_group_accuracy_columns(df, groups):
    score_cols = df.filter(regex=r"^点数\d+$").columns

    # build a DataFrame of new acc_ columns and concat once to avoid fragmentation
    new_cols = {}
    for (start, end, label, color) in groups:
        s = start - 1
        e = end
        cols = score_cols[s:e]
        new_cols[f"acc_{label}"] = df[cols].mean(axis=1)

    new_df = pd.DataFrame(new_cols, index=df.index)
    df = pd.concat([df, new_df], axis=1)
    return df


def plot_dual_level(df_win, df_wo, groups, level_col, save_name):
    acc_cols = [f"acc_{g[2]}" for g in groups]
    x_labels = [g[2] for g in groups]
    x = range(len(x_labels))

    win_mean = df_win.groupby(level_col)[acc_cols].mean()
    wo_mean  = df_wo.groupby(level_col)[acc_cols].mean()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

    # draw lines per level but break between movies (no connecting across movie boundaries)
    movie_ranges = [(0, 1), (2, 3), (4, 5)]

    # create a consistent color mapping for each level so colors are same across movies and subplots
    levels = list(win_mean.index)
    cmap = plt.get_cmap('tab10')
    color_map = {lvl: cmap(i % cmap.N) for i, lvl in enumerate(levels)}

    for lvl, row in win_mean.iterrows():
        vals = row.values
        color = color_map[lvl]
        for (s, e) in movie_ranges:
            ax1.plot(list(range(s, e+1)), vals[s:e+1], marker="o", color=color, label=f"{level_col} {lvl}" if s==movie_ranges[0][0] else None)

    # plot overall mean for win, segmented per movie
    mean_win_vals = win_mean.mean(axis=0).values
    for (s, e) in movie_ranges:
        ax1.plot(list(range(s, e+1)), mean_win_vals[s:e+1], linestyle="--", color="black", linewidth=3, label="平均（告知）" if s==movie_ranges[0][0] else None)

    ax1.set_title(f"告知：{level_col}ごとの平均正答率")
    ax1.set_ylabel("正答率")
    ax1.set_ylim(0, 1)
    ax1.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=LEGEND_FONT_SIZE)

    for lvl, row in wo_mean.iterrows():
        vals = row.values
        color = color_map.get(lvl, cmap(0))
        for (s, e) in movie_ranges:
            ax2.plot(list(range(s, e+1)), vals[s:e+1], marker="o", color=color, label=f"{level_col} {lvl}" if s==movie_ranges[0][0] else None)

    # plot overall mean for wo, segmented per movie
    mean_wo_vals = wo_mean.mean(axis=0).values
    for (s, e) in movie_ranges:
        ax2.plot(list(range(s, e+1)), mean_wo_vals[s:e+1], linestyle="--", color="black", linewidth=3, label="平均（未告知）" if s==movie_ranges[0][0] else None)

    ax2.set_title(f"未告知：{level_col}ごとの平均正答率")
    ax2.set_ylabel("正答率")
    ax2.set_ylim(0, 1)
    ax2.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=LEGEND_FONT_SIZE)

    # align rotated labels and adjust margins to avoid clipping
    plt.xticks(list(x), x_labels, rotation=30, ha='right', rotation_mode='anchor')
    fig.subplots_adjust(bottom=0.30, right=0.78)
    plt.tight_layout()
    plt.savefig(save_name, dpi=300, bbox_inches="tight")
    plt.show()


def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")
    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo  = load_sheet(data_path, sheet_name="未告知")

    df_win = add_group_accuracy_columns(df_win, groups)
    df_wo  = add_group_accuracy_columns(df_wo, groups)

    plot_dual_level(df_win, df_wo, groups, level_col="HAレベル", save_name=output_file_path("HAレベルvs正答率.png"))
    plot_dual_level(df_win, df_wo, groups, level_col="VFレベル", save_name=output_file_path("VFレベルvs正答率.png"))


if __name__ == "__main__":
    main()
