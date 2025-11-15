"""映画別 × 高低（6区間）で個人ごとの正答率をプロットするスクリプト

使い方: このファイルを実行すると `データ_edit.xlsx` の `告知`/`未告知` シートを読み込み、
図を `感覚記憶中の強度vs正答率_movie_groups.png` として保存します。
"""
import matplotlib.pyplot as plt
import mplcursors
from analysis_utils import load_sheet, groups, data_file_path, output_file_path, ensure_data_dir, ANNOTATION_FONT_SIZE, LEGEND_FONT_SIZE


def plot_group_accuracy(df, ax, title, show_legend=True):
    score_cols = df.filter(regex=r"^点数\d+$").columns

    # 各区間の正答率
    acc_results = []
    for (start, end, label, color) in groups:
        s = start - 1
        e = end
        cols = score_cols[s:e]
        acc = df[cols].mean(axis=1)
        acc_results.append({"label": label, "accuracy": acc, "color": color})

    x_labels = [g[2] for g in groups]
    x = list(range(len(groups)))

    # 個人ライン（色分けして凡例に氏名を表示）
    lines = []
    name_list = []
    cmap = plt.get_cmap("tab20")
    n = len(df)

    # 個人ライン（映画ごとに線を分断して描画：映画1は点0-1, 映画2は2-3, 映画3は4-5）
    movie_ranges = [(0, 1), (2, 3), (4, 5)]
    for i, row in df.iterrows():
        y_all = [g["accuracy"].iloc[i] for g in acc_results]
        name = row.get("姓名（漢字）", f"# {i}")
        color = cmap(i % cmap.N)
        # plot segments per movie
        for (s, e) in movie_ranges:
            xs = x[s:e+1]
            ys = y_all[s:e+1]
            line, = ax.plot(xs, ys, color=color, alpha=0.9)
            # only append legend entry once (for the first segment)
            if s == movie_ranges[0][0]:
                line.set_label(name)
                lines.append(line)
                name_list.append(name)

    # 平均線（統一スタイル）
    means = [g["accuracy"].mean() for g in acc_results]
    # plot mean with same segmentation (no cross-movie connecting lines)
    for (s, e) in movie_ranges:
        xs = x[s:e+1]
        ys = means[s:e+1]
        ax.plot(xs, ys, linestyle="--", linewidth=3, color="black", label="平均" if s==movie_ranges[0][0] else None)
    # 凡例は右外に出す（氏名が多い場合に見やすくする）
    if show_legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=LEGEND_FONT_SIZE)

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=30, ha='right')
    ax.set_ylim(0, 1)
    ax.set_ylabel("正答率")
    ax.set_title(title)

    cursor = mplcursors.cursor(lines, hover=True)

    @cursor.connect("add")
    def on_hover(sel):
        idx = lines.index(sel.artist)
        name = name_list[idx]
        val = sel.target[1]
        sel.annotation.set(
            text=f"{name}\n正答率: {val:.3f}",
            fontsize=ANNOTATION_FONT_SIZE,
            bbox=dict(boxstyle="round", fc="white", ec="gray")
        )


def main():
    # Ensure data directory exists (user should place the original Excel here)
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")
    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo  = load_sheet(data_path, sheet_name="未告知")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

    plot_group_accuracy(df_win,  ax1, "告知：映画別 × 高低 × 正答率", show_legend=True)
    plot_group_accuracy(df_wo,   ax2, "未告知：映画別 × 高低 × 正答率", show_legend=False)

    # adjust margins so slanted x-labels and external legends are not cut off
    # increase bottom margin and right margin to avoid clipping of slanted x-labels and external legend
    fig.subplots_adjust(bottom=0.30, right=0.78)
    plt.tight_layout()
    out = output_file_path("感覚記憶中の強度vs正答率_movie_groups.png")
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
