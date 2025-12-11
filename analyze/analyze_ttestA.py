import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path
import japanize_matplotlib
from scipy import stats
from typing import Optional

# 表示制御: False にすると図は表示されず自動で閉じられます
SHOW_FIGURES = False
# 図の自動保存先（リポジトリ直下の `analyze/outputs/`）
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SAVE_DPI = 300

df = pd.read_excel(r"../data/data_refactored.xlsx")

# 感覚記憶の強度分布

# 1低：1–20
# 1高：21–37
# 2低：38–62
# 2高：63–92
# 3低：93–118
# 3高：119–134

print(df.head())

#    sum_point  is_告知 name                          e_mail sex  ages  VF_level  ...  Q_order70_confidence  Q_order71_options Q_order71_score  Q_order71_confidence  Q_order72_options Q_order72_score  Q_order72_confidence
# 0        147   True   翟辉  25l1a004@student.gs.chiba-u.jp   男  26.0         1  ...                     7               选项 2               1                     7               选项 2               0                     7
# 1        112   True   蔡逸             caiyi0128@gmail.com   男  25.0         5  ...                     4               选项 1               0                     1               选项 1               1                     6
# 2        157   True  孟欣雨           mengxinyu81@gmail.com   女  25.0         3  ...                     4               选项 2               1                     6               选项 2               0                     
# 5
# 3        124   True  于穆涵            muhan_yu@outlook.com   女  27.0         3  ...                     1               选项 1               0                     1               选项 1               1                     
# 1
# 4        125   True  董熙莹          dongxiying47@gmail.com   女  27.0         2  ...                     7               选项 2               1                     7               选项 1               1                     
# 7

# [5 rows x 627 columns]


# 問題番号と強度ラベルのマッピングを作成。
df_map = pd.DataFrame({
	"item_id": list(range(1, 135)),
	"intensity": (
		["low"] * 20 + ["high"] * 17 +
		["low"] * 25 + ["high"] * 30 +
		["low"] * 26 + ["high"] * 16
	)
})	

print(df_map.head())

df_map_local = df_map[["item_id", "intensity"]]
# Melt data to long format
df_long = pd.melt(
	df,
	id_vars=["name", "is_告知"],
	value_vars=[f"Q_sensory{i}_score" for i in range(1, 135)],
	var_name="question",
	value_name="correct"
)
# Extract item_id from question column
df_long["item_id"] = df_long["question"].str.extract(r"Q_sensory(\d+)_score").astype(int)
# Merge with intensity mapping
df_long = df_long.merge(df_map_local, on="item_id", how="left")
print(df_long.head(20))

# 分析 A：告知条件を無視した被験者内の対応のある t 検定
# - 手順:
# 	1. 集約データをワイド形式に変換（被験者ごとに1行）。列として `accuracy_low`（低情動下の正答率）、`accuracy_high`（高情動下の正答率） を作成。
# 	2. `accuracy_low` vs `accuracy_high` に対して対応のある t 検定（paired t-test）を実行。
# - 出力:
# 	- t 値、自由度 df、p 値
# 	- 効果量（Cohen's d）
# 	- 各条件の平均値（M）と標準偏差（SD）


# 1. 集約データをワイド形式に変換
agg = df_long.groupby(["name", "intensity"])["correct"].mean().reset_index()
paired_wide = agg.pivot(index="name", columns="intensity", values="correct").reset_index()
print(paired_wide.head())
# 2. 対応のある t 検定を実行
low_scores = paired_wide["low"].dropna()
high_scores = paired_wide["high"].dropna()
# 両条件でデータが存在する被験者のみを対象にする
common_indices = low_scores.index.intersection(high_scores.index)
low_common = low_scores.loc[common_indices]
high_common = high_scores.loc[common_indices]
t_stat, p_value = stats.ttest_rel(low_common, high_common)
# 効果量（Cohen's d）
diffs = low_common - high_common
cohen_d = diffs.mean() / diffs.std(ddof=1)
# 各条件の平均値と標準偏差
mean_low = low_common.mean()
std_low = low_common.std(ddof=1)
mean_high = high_common.mean()
std_high = high_common.std(ddof=1)
# 結果の表示
with open(OUTPUT_DIR / "ttestA_results.txt", "w", encoding="utf-8") as f:
	f.write(f"Paired t-test results:\n")
	f.write(f"t({len(common_indices)-1}) = {t_stat:.4f}, p = {p_value:.4f}\n")
	f.write(f"Cohen's d = {cohen_d:.4f}\n")
	f.write(f"Low intensity: M = {mean_low:.4f}, SD = {std_low:.4f}\n")
	f.write(f"High intensity: M = {mean_high:.4f}, SD = {std_high:.4f}\n")
	f.write(f"結論: {'有意差あり' if p_value < 0.05 else '有意差なし'}\n")

# なぜペア30になるのか？
# low/high 両条件でデータが存在する被験者数だから


# Visualization
plt.figure(figsize=(6, 4))
plt.boxplot([low_common, high_common], labels=["Low Intensity", "High Intensity"])
plt.ylabel("Accuracy")
plt.title("Paired t-test: Low vs High Intensity")
plt.tight_layout()
# 自動保存
out_path = OUTPUT_DIR / "ttestA_boxplot.png"
plt.savefig(out_path, dpi=SAVE_DPI)
print(f"Saved figure: {out_path}")
if SHOW_FIGURES:
	plt.show()
plt.close()
# ==============================================================================


# Visualization2: ペアごとの線グラフ
plt.figure(figsize=(6, 4))
for _, row in paired_wide.iterrows():
	if pd.notna(row["low"]) and pd.notna(row["high"]):
		plt.plot(
			["Low Intensity", "High Intensity"],
			[row["low"], row["high"]],
			marker="o",
			color="gray",
			alpha=0.6,
		)
# グランド平均を追加
mean_low_overall = low_common.mean()
mean_high_overall = high_common.mean()
plt.plot(
	["Low Intensity", "High Intensity"],
	[mean_low_overall, mean_high_overall],
	marker="o",
	linewidth=3,
	color="black"
)
plt.ylabel("Accuracy")
plt.title("Within-Subject Change: Low vs High Intensity")
plt.tight_layout()
# 自動保存
out_path2 = OUTPUT_DIR / "ttestA_paired_lines.png"
plt.savefig(out_path2, dpi=SAVE_DPI)
print(f"Saved figure: {out_path2}")
if SHOW_FIGURES:
	plt.show()
plt.close()
# ==============================================================================