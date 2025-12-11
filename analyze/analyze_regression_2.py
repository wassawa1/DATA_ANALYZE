import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path
import japanize_matplotlib

# 表示制御: False にすると図は表示されず自動で閉じられます
SHOW_FIGURES = False
# 図の自動保存先（リポジトリ直下の `outputs/`）
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "analyze" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SAVE_DPI = 300

# Deta view
# sum_point	is_告知	name	e_mail	sex	ages	VF_level	is_HA_scary	HA_level	Q_sensory1_options	Q_sensory1_score	Q_sensory1_confidence	Q_sensory2_options	Q_sensory2_score	Q_sensory2_confidence	Q_sensory3_options	Q_sensory3_score	Q_sensory3_confidence
# 147	TRUE	翟辉	25l1a004@student.gs.chiba-u.jp	男	26	1	FALSE	2	金色	1	5	烟草	1	7	红色	1	7
# 112	TRUE	蔡逸	caiyi0128@gmail.com	男	25	5	TRUE	4	金色	1	5	墨镜	0	6	红色	1	4
# 157	TRUE	孟欣雨	mengxinyu81@gmail.com	女	25	3	TRUE	3	金色	1	7	烟草	1	4	红色	1	6
# 124	TRUE	于穆涵	muhan_yu@outlook.com	女	27	3	TRUE	3	棕黑色	0	2	烟草	1	2	红色	1	1
# 125	TRUE	董熙莹	dongxiying47@gmail.com	女	27	2	TRUE	3	棕黑色	0	1	烟草	1	6	红色	1	3
# 137	TRUE	王亚泽	wyz215750837@gmail.com	男	29	2	TRUE	4	金色	1	6	墨镜	0	3	红色	1	7

df = pd.read_excel(r"../data/data_refactored.xlsx")
print(df.head())

# memory_type ごとに分け、それぞれに対して平均値を計算しておく。列名にaccuracy_sensory, accuracy_orderを付与

# モデル2：記憶タイプと告知条件およびその交互作用を含める
# - `accuracy ~ C(memory_type) * C(expectancy)`

# モデル2：記憶タイプと告知条件およびその交互作用を含める
# - `accuracy ~ C(memory_type) * C(is_告知)`

# Build column lists safely
sensory_cols = [
	f"Q_sensory{i}_score"
	for i in range(1, 135)
	if f"Q_sensory{i}_score" in df.columns
]
order_cols = [
	f"Q_order{i}_score"
	for i in range(1, 73)
	if f"Q_order{i}_score" in df.columns
]

# Per-subject mean accuracy
df_summary = pd.DataFrame({
	"subject": df["name"],
	"is_告知": df["is_告知"],
	"accuracy_sensory": df[sensory_cols].mean(axis=1),
	"accuracy_order": df[order_cols].mean(axis=1),
})

# Wide -> long
df_long = df_summary.melt(
	id_vars=["subject", "is_告知"],
	value_vars=["accuracy_sensory", "accuracy_order"],
	var_name="memory_type",
	value_name="accuracy",
)

# Clean factor labels
df_long["memory_type"] = df_long["memory_type"].map({
	"accuracy_sensory": "sensory",
	"accuracy_order": "order",
})

# Force reference category to sensory (optional but clearer)
df_long["memory_type"] = pd.Categorical(
	df_long["memory_type"],
	categories=["sensory", "order"]
)

# Linear regression: memory_type, is_告知, and their interaction
model2 = smf.ols(
	"accuracy ~ C(memory_type) * C(is_告知)",
	data=df_long
).fit(
	cov_type="cluster",
	cov_kwds={"groups": df_long["subject"]}
)

with open(OUTPUT_DIR / "analyze_output_model2.txt", "w", encoding="utf-8") as f:
	print(model2.summary(), file=f)

# -------------------------
# Visualization: Boxplot by memory_type and is_告知
# -------------------------
fig, ax = plt.subplots(figsize=(8, 6))
df_long.boxplot(
	column="accuracy",
	by=["memory_type", "is_告知"],
	ax=ax
)
ax.set_title("Accuracy by Memory Type and 告知条件")
ax.set_ylabel("Accuracy")
plt.suptitle("")
plt.tight_layout()
out_path = OUTPUT_DIR / "boxplot_accuracy_model2.png"
fig.savefig(out_path, dpi=SAVE_DPI, bbox_inches="tight")
print(f"Saved figure: {out_path}")
if SHOW_FIGURES:
	plt.show()
plt.close(fig)

# -----------------------------------------
# Visualization: Paired plot within subjects(color by is_告知)
fig, ax = plt.subplots(figsize=(8, 6))
for key, grp in df_long.groupby("subject"):
	ax.plot(
		grp["memory_type"],
		grp["accuracy"],
		color="gray" if grp["is_告知"].iloc[0] else "blue",
		alpha=0.5,
		marker="o"
	)
ax.set_title("Paired Accuracy by Memory Type within Subjects")
ax.set_ylabel("Accuracy")
plt.tight_layout()
plt.legend(["告知", "未告知"], title="条件", loc="upper left")
out_path2 = OUTPUT_DIR / "paired_within_subjects_model2.png"
fig.savefig(out_path2, dpi=SAVE_DPI, bbox_inches="tight")
print(f"Saved figure: {out_path2}")
if SHOW_FIGURES:
	plt.show()
plt.close(fig)
# -----------------------------------------

# 以下に2点の結果を確認

#   - 記憶タイプの主効果（順序記憶が感覚記憶より高いか）
#   - 告知条件の主効果
#   - 両者の交互作用の有意性

# これらの結果は、`analyze_output_model2.txt` に保存されています
# ==============================================================================
# Dep. Variable:               accuracy   R-squared:                       0.327
# Model:                            OLS   Adj. R-squared:                  0.290
# Method:                 Least Squares   F-statistic:                     22.77
# Date:                Thu, 11 Dec 2025   Prob (F-statistic):           8.92e-08
# Time:                        21:28:15   Log-Likelihood:                 64.348
# No. Observations:                  60   AIC:                            -120.7
# Df Residuals:                      56   BIC:                            -112.3
# Df Model:                           3                                         
# Covariance Type:              cluster                                         
# ============================================================================================================
#                                                coef    std err          z      P>|z|      [0.025      0.975]
# ------------------------------------------------------------------------------------------------------------
# Intercept                                    0.5954      0.026     23.008      0.000       0.545       0.646
# C(memory_type)[T.order]                      0.1129      0.025      4.603      0.000       0.065       0.161
# C(is_告知)[T.True]                            -0.0046      0.030     -0.152      0.880      -0.064       0.055
# C(memory_type)[T.order]:C(is_告知)[T.True]     0.0047      0.030      0.157      0.875      -0.054       0.063
# ==============================================================================
# Omnibus:                        5.735   Durbin-Watson:                   2.070
# Prob(Omnibus):                  0.057   Jarque-Bera (JB):                4.798
# Skew:                           0.647   Prob(JB):                       0.0908
# Kurtosis:                       3.494   Cond. No.                         6.85
# ==============================================================================

# Notes:
# [1] Standard Errors are robust to cluster correlation (cluster)

# 結論:以上の結果から、
# C(memory_type)の主効果は、p < 0.001で有意であり、順序記憶の方が感覚記憶よりも正答率が高いことが示された。
# 一方、C(is_告知)の主効果および交互作用効果は有意ではなく、告知条件が正答率に与える影響は見られなかった。
# 両者の交互作用も、p = 0.875で有意ではなかった。
# これにより、記憶タイプが正答率に影響を与える主要な要因であることが示唆された。

