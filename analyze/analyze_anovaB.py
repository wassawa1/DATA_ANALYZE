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


# 分析 B：強度 × 告知 の 2×2 混合 ANOVA
# - 長形式データを用いて混合 ANOVA を実行します：
# 	- 被説明変数: `accuracy`
# 	- 被験者内要因（within）: `intensity`（`low` / `high`）
# 	- 被験者間要因（between）: `expectancy`（0 / 1）これはis_告知のこと。
# 	- 被験者識別子: `subject_id`

# ※accruracyは平均値です。算出してください。

df_summary = pd.DataFrame()
df_summary["accuracy_sensory"] = df[[f"Q_sensory{i}_score" for i in range(1, 135)]].mean(axis=1)
df_summary["accuracy_order"] = df[[f"Q_order{i}_score" for i in range(1, 73)]].mean(axis=1)
df_summary["is_告知"] = df["is_告知"]
df_summary["name"] = df["name"]
print(df_summary.head())

# Merge accuracy back to long format
df_long = df_long.merge(
	df_summary[["name", "accuracy_sensory", "accuracy_order"]],
	on="name",
	how="left"
)
# Use accuracy_sensory as the dependent variable
# Coerce is_告知 to expectancy 0/1
df_long["expectancy"] = df_long["is_告知"].astype(int)
# Subject ID
df_long["subject_id"] = df_long["name"]
# Fit mixed effects model

model = smf.mixedlm(
	"accuracy_sensory ~ C(intensity) * C(expectancy)",
	data=df_long,
	groups=df_long["subject_id"],
	re_formula="~C(intensity)"
)
result = model.fit()


with open(OUTPUT_DIR / "anovaB_results.txt", "w", encoding="utf-8") as f:
	f.write(result.summary().as_text())

# 結果の解釈:
# - `C(intensity)[T.high]`: 強度の主効果（low vs high）
# - `C(expectancy)[T.1]`: 告知の主効果（0 vs 1）
# - `C(intensity)[T.high]:C(expectancy)[T.1]`: 強度と告知の交互作用	
# - p 値が 0.05 未満であれば統計的に有意と判断します。	
# - 効果量の計算には追加の手順が必要です（ここでは省略します）。
# - 各条件の平均値と標準偏差も計算して報告します。
grouped = df_long.groupby(["intensity", "expectancy"])["correct"]
summary_stats = grouped.agg(['mean', 'std', 'count']).reset_index()
print("\n各条件の平均値と標準偏差:")
print(summary_stats)

#                       Mixed Linear Model Regression Results
# ==================================================================================
# Model:                    MixedLM       Dependent Variable:       accuracy_sensory
# No. Observations:         4020          Method:                   REML            
# No. Groups:               30            Scale:                    0.0000          
# Min. group size:          134           Log-Likelihood:           64063.5652      
# Max. group size:          134           Converged:                Yes             
# Mean group size:          134.0                                                   
# ----------------------------------------------------------------------------------
#                                        Coef.  Std.Err.    z    P>|z| [0.025 0.975]
# ----------------------------------------------------------------------------------
# Intercept                               0.593    0.002 335.416 0.000  0.590  0.596
# C(intensity)[T.low]                    -0.000    0.000  -0.066 0.948 -0.000  0.000
# C(expectancy)[T.1]                     -0.004    0.002  -1.580 0.114 -0.009  0.001
# C(intensity)[T.low]:C(expectancy)[T.1]  0.000    0.000   0.012 0.991 -0.000  0.000
# Group Var                               0.000   43.978                            
# Group x C(intensity)[T.low] Cov         0.000    0.414                            
# C(intensity)[T.low] Var                 0.000                                     
# ==================================================================================


# 以上から以下のことが言える
# - 強度の主効果は有意ではない (p = 0.948)
# - 告知の主効果も有意ではない (p = 0.114)
# - 交互作用も有意ではない (p = 0.991)
# - 強度の主効果: p = 0.354（有意ではない）
# これらの結果を踏まえ、強度と告知のいずれも正答率に有意な影響を与えなかったと言えます。


# Visualization: boxplot by intensity and expectancy
ax = plt.figure(figsize=(8, 6)).gca()
df_long.boxplot(
	column="accuracy_sensory",
	by=["intensity", "expectancy"],
	ax=ax
)
ax.set_title("Accuracy by Intensity and Expectancy")
ax.set_ylabel("Accuracy")
plt.suptitle("")
plt.tight_layout()
# 自動保存
out_path = OUTPUT_DIR / "anovaB_boxplot.png"
ax.get_figure().savefig(out_path, dpi=SAVE_DPI, bbox_inches="tight")
print(f"Saved figure: {out_path}")
if SHOW_FIGURES:
	plt.show()
plt.close(ax.get_figure())
# ==============================================================================