我有一份情绪记忆实验的数据，想用 Python 做回归分析，研究「记忆类型（感官 vs 顺序）」和「告知条件（告知 vs 未告知）」对正确率的影响。

### 一、数据结构（原始层面）
目前我的原始数据表中，每一行是“被试 × 题目”的作答记录，列大致如下：
- subject_id：被试编号
- item_id：题目编号（1–134 是感官细节记忆题，135–206 是顺序记忆题）
- correct：该题作答是否正确（1=正确，0=错误）
- expectancy：告知条件（0=未告知，1=告知）

### 二、数据预处理要求
1. 先根据 item_id 生成一个新的分类变量 memory_type：
   - 如果 item_id 在 1〜134 之间，memory_type = "verbatim"
   - 如果 item_id 在 135〜206 之间，memory_type = "order"

2. 然后把数据从“题目层面”聚合到“被试 × 记忆类型 × 告知条件”的层面，计算每个被试在每种条件下的正确率：
   - groupby(subject_id, memory_type, expectancy)，对 correct 取平均，得到 accuracy（0〜1）

最终得到一个长格式的数据框，列至少包括：
- subject_id
- memory_type （"verbatim" or "order"）
- expectancy （0 or 1）
- accuracy （该被试在该类型 × 告知条件下的正确率）

### 三、回归分析模型
在聚合后的数据上做线性回归，用 statsmodels 之类的包：

模型 1：只看记忆类型主效应
- accuracy ~ C(memory_type)

模型 2：同时考虑记忆类型和告知条件，以及它们的交互
- accuracy ~ C(memory_type) * C(expectancy)

其中：
- C(memory_type) 是分类变量（感官 vs 顺序）
- C(expectancy) 是分类变量（告知 vs 未告知）
- 重点关注：
  - 记忆类型的主效应系数（顺序记忆是否高于感官记忆）
  - 告知条件的主效应
  - 二者的交互项是否显著

### 四、输出
1. 输出每个模型的回归系数、标准误、t 值、p 值、R²。
2. 把结果整理成可以直接写进论文的形式，例如：
   - 记忆类型主效应显著（順序 > 感覚）：β = ..., t = ..., p = ...
   - 告知条件主效应是否显著
   - 交互作用是否显著
3. 画一个交互作用图（memory_type × expectancy 对 accuracy 的折线图或柱状图），方便我放进论文。