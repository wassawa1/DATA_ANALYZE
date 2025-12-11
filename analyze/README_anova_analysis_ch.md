三、感官记忆整体正确率vs高低情感（电影1,2,3低vs电影1,2,3，高）
我有一份情绪记忆实验的数据，想用 Python 做统计分析，检验
「在感官细节记忆题中，高 vs 低 情绪强度是否影响正确率」，并考察告知条件的影响。
 
### 一、数据结构（原始层面）
 
目前原始数据表中，每一行是“被试 × 题目”的作答记录，列大致如下：
 
- subject_id：被试编号
- item_id：题目编号
- correct：该题作答是否正确（1=正确，0=错误）
- expectancy：告知条件（0=未告知，1=告知）
- memory_type：记忆类型（"verbatim"＝感官细节记忆，"order"＝顺序记忆）
 （如果暂时没有这一列，可以根据题号生成：1〜134 为 "verbatim"，135〜206 为 "order"）
 
另外，我需要一个情绪强度变量 intensity：
- low：低情绪强度（电影 1,2,3 的低强度片段）
- high：高情绪强度（电影 1,2,3 的高强度片段）
 
如果现在数据里已经有 intensity 这一列，就直接使用；
如果没有，请根据我提供的 “题号—影片/强度” 对应表来生成（我会补充映射规则）。
 
 
### 二、数据前处理
 
1. 只保留感官记忆题目：
  - 过滤 memory_type == "verbatim"
 
2. 为每个作答记录生成情绪强度变量 intensity：
  - intensity = "low" 或 "high"
  - 具体规则按我补充的题号映射来实现
 
3. 将数据从 “题目层面” 聚合到 “被试 × 情绪强度 × 告知条件” 层面，
  对每个被试在每种情绪强度下的正答率进行计算：
 
  - groupby(subject_id, intensity, expectancy)，
    对 correct 取平均，生成 accuracy（0〜1）
 
得到一个长格式数据框，包含至少以下列：
- subject_id
- intensity（"low" or "high"）
- expectancy（0 or 1）
- accuracy（该被试在该情绪强度 × 告知条件下的正确率）
 
 
### 三、统计分析
 
请用 statsmodels 或 pingouin 等包，按下面两个层次做分析。
 
#### 分析 A：忽略告知条件，先做被试内配对 t 检验
 
1. 把聚合后的数据 pivot 成“每个被试一行”的宽格式：
  - 一列是 accuracy_low（该被试在 low 条件的正确率）
  - 一列是 accuracy_high（该被试在 high 条件的正确率）
 
2. 对 accuracy_low vs accuracy_high 做配对 t 检验（paired t-test）：
  - 输出 t 值、df、p 值、效果量 Cohen's d
  - 把均值和标准差也算出来（low/high 各自的 mean, SD）
 
#### 分析 B：强度 × 告知 条件的 2×2 混合 ANOVA
 
在长格式数据上，进行混合 ANOVA：
 
- 因变量：accuracy
- 被试内要因：intensity（low/high）
- 被试间要因：expectancy（告知/未告知）
 
模型示例（用 pingouin）：
- mixed_anova(dv='accuracy', within='intensity', between='expectancy', subject='subject_id', data=df)
 
请报告：
- intensity 的主效应（情绪强度的影响是否显著）
- expectancy 的主效应（告知条件是否显著）
- intensity × expectancy 的交互作用是否显著
 
同时提供：
- 各主效应和交互项的 F 值、df、p 值、部分 eta²（partial η²）
 
 
### 四、输出与整理
 
1. 输出：
  - 配对 t 检验的 t, df, p, Cohen's d
  - 混合 ANOVA 的 F, df, p, partial η²
  - 每个条件的描述统计量（均值 M、标准差 SD）：
    - low / high 情绪强度下的 accuracy 平均值和 SD
    - 如有可能，可按告知/未告知分别给出
 
2. 请帮我整理成可以直接写进论文结果部分的句子模板，例如：
  - 「低情緒強度条件の感覚記憶正答率（M=..., SD=...）は，高情緒強度条件（M=..., SD=...）よりも有意に高かった，t(df)=..., p=..., d=...。」
  - 「混合 ANOVA の結果，情緒強度の主効果が有意であった（F(...)=..., p=..., η²=...）。告知条件の主効果は有意ではなく，交互作用も認められなかった（F(...)=..., p>...）。」
 
3. 画一张柱状图或折线图：
  - X 轴：情绪强度（low / high）
  - Y 轴：accuracy
  - 可按告知条件（expectancy）分色或分线，用于论文插图。