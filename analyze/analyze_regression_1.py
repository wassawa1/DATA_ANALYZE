import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path

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
# memory_typeは列のQ_sensory1_score ～ Q_sensory134_scoreまで
# order_typeは列のQ_order1_score ～ Q_order72_scoreまで
df_sensory = df[[f"Q_sensory{i}_score" for i in range(1, 135)]]
df_order = df[[f"Q_order{i}_score" for i in range(1, 73)]]

df_summary = pd.DataFrame()
df_summary["accuracy_sensory"] = df_sensory.mean(axis=1)
df_summary["accuracy_order"] = df_order.mean(axis=1)
df_summary["is_告知"] = df["is_告知"]
df_summary["name"] = df["name"]

print(df_summary.head())


# # モデル1：記憶タイプの主効果のみを見る
# # - `accuracy ~ C(memory_type)` memory_type: sensory, order

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
    "accuracy_sensory": df[sensory_cols].mean(axis=1),
    "accuracy_order": df[order_cols].mean(axis=1),
})

# Wide -> long
df_long = df_summary.melt(
    id_vars=["subject"],
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

# Linear regression: main effect of memory_type
# Use cluster-robust SE by subject to handle repeated measures
model = smf.ols(
    "accuracy ~ C(memory_type)",
    data=df_long
).fit(
    cov_type="cluster",
    cov_kwds={"groups": df_long["subject"]}
)

with open(OUTPUT_DIR / "analyze_output_model1.txt", "w", encoding="utf-8") as f:
	print(model.summary(), file=f)

# -------------------------
# Visualization 1: Boxplot
# -------------------------
ax = df_summary[["accuracy_sensory", "accuracy_order"]].plot(
    kind="box",
    figsize=(8, 6)
)
ax.set_title("Accuracy by Memory Type")
ax.set_ylabel("Accuracy")
ax.set_xticklabels(["Sensory", "Order"])
ax.grid(axis="y")
plt.tight_layout()
# 自動保存
out_path = OUTPUT_DIR / "boxplot_accuracy_model1.png"
ax.get_figure().savefig(out_path, dpi=SAVE_DPI, bbox_inches="tight")
print(f"Saved figure: {out_path}")
if SHOW_FIGURES:
    plt.show()
plt.close(ax.get_figure())

# -----------------------------------------
# Visualization 2: Paired lines per subject
# -----------------------------------------


# Prepare paired data in consistent order
paired = df_summary.dropna(subset=["accuracy_sensory", "accuracy_order"]).copy()

fig, ax = plt.subplots(figsize=(8, 6))
# Draw one line per subject
for _, row in paired.iterrows():
    ax.plot(
        ["Sensory", "Order"],
        [row["accuracy_sensory"], row["accuracy_order"]],
        marker="o",
        color="gray",
        alpha=0.6,
    )

# Add grand means
mean_s = paired["accuracy_sensory"].mean()
mean_o = paired["accuracy_order"].mean()
ax.plot(["Sensory", "Order"], [mean_s, mean_o], marker="o", linewidth=3, color="black")

ax.set_title("Within-Subject Change: Sensory vs Order")
ax.set_ylabel("Accuracy")
ax.grid(axis="y")
plt.tight_layout()
# 自動保存
out_path2 = OUTPUT_DIR / "paired_within_subjects_model1.png"
fig.savefig(out_path2, dpi=SAVE_DPI, bbox_inches="tight")
print(f"Saved figure: {out_path2}")
if SHOW_FIGURES:
    plt.show()
plt.close(fig)