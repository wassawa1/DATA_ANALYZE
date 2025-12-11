# 三、感覚記憶の正答率 vs 高低情動（映画1,2,3 の低 vs 高）

以下は、感情記憶実験データを用いて「感覚的詳細記憶（verbatim）」において高情動／低情動が正答率に影響を及ぼすか、また告知条件がそれにどう影響するかを検定するための要件・手順の日本語訳です。

1. 目的
- 感覚的詳細記憶問題に限定して、低強度（low）と高強度（high）の情動刺激間で正答率（accuracy）に差があるかを検定する。
- さらに、告知条件（expectancy: 告知 vs 未告知）がこの差に影響するかを混合因子解析（強度 × 告知）で検討する。

2. データ構造（原始レベル）

現在の生データは1行が「被験者 × 問題」の解答記録になっており、最低限以下の列があることを想定します：
- `subject_id`：被験者識別子
- `item_id`：問題番号
- `correct`：その問題の正否（1 = 正解、0 = 不正解）
- `expectancy`：告知条件（0 = 未告知、1 = 告知）
- `memory_type`：記憶タイプ（`verbatim` = 感覚詳細、`order` = 順序）

注：もし `memory_type` 列が存在しない場合は `item_id` に基づいて生成します（例：1〜134 → `verbatim`、135〜206 → `order`）。

さらに、情動強度変数 `intensity` を用意します：
- `low`：低情動強度（映画1,2,3 の低強度片）
- `high`：高情動強度（映画1,2,3 の高強度片）

この `intensity` 列が既にデータ中にある場合はそれを用い、ない場合はユーザが提供する「題号 ↔ 映画/強度」マッピング規則に従って `item_id` から `intensity` を生成します。

3. データ前処理（手順）

1) 感覚記憶問題のみを抽出
- フィルタ: `memory_type == "verbatim"`

2) `intensity` を付与
- 既存列がなければ、提供される題号→(映画, 強度) マッピングに基づいて `intensity` を `low` / `high` として付与する。

3) 被験者 × 情動強度 × 告知条件 レベルへ集約
- groupby(`subject_id`, `intensity`, `expectancy`) のうえで `correct` の平均をとり、各セルの `accuracy` を算出（0〜1）。

出力されるロングフォーマットのデータフレームは少なくとも以下の列を含みます：
- `subject_id`
- `intensity`（`low` / `high`）
- `expectancy`（0 / 1）
- `accuracy`（該当被験者の該当条件における正答率）

4. 統計解析

以下の2段階で解析を行います（`statsmodels` や `pingouin` などを利用）：

分析 A：告知条件を無視した被験者内の対応のある t 検定
- 手順:
	1. 集約データをワイド形式に変換（被験者ごとに1行）。列として `accuracy_low`（低情動下の正答率）、`accuracy_high`（高情動下の正答率） を作成。
	2. `accuracy_low` vs `accuracy_high` に対して対応のある t 検定（paired t-test）を実行。
- 出力:
	- t 値、自由度 df、p 値
	- 効果量（Cohen's d）
	- 各条件の平均値（M）と標準偏差（SD）

分析 B：強度 × 告知 の 2×2 混合 ANOVA
- 長形式データを用いて混合 ANOVA を実行します：
	- 被説明変数: `accuracy`
	- 被験者内要因（within）: `intensity`（`low` / `high`）
	- 被験者間要因（between）: `expectancy`（0 / 1）
	- 被験者識別子: `subject_id`
- 例（pingouin を利用する場合）:
	- `mixed_anova(dv='accuracy', within='intensity', between='expectancy', subject='subject_id', data=df_long)`
- 出力:
	- `intensity` の主効果（F, df, p, partial η²）
	- `expectancy` の主効果（F, df, p, partial η²）
	- `intensity × expectancy` の交互作用（F, df, p, partial η²）

5. 出力と整理（レポート用）

1) 必要な数値出力
- 対応のある t 検定: t, df, p, Cohen's d
- 混合 ANOVA: 各主効果と交互作用の F, df, p, partial η²
- 各条件の記述統計（平均 M, 標準偏差 SD）: 全体の low / high、および可能であれば告知別（expectancy = 0 / 1）に分けた M, SD

2) 論文向けの文例テンプレート（日本語）
- 例（対応 t 検定の記述）:
	- 「低情動強度条件における感覚的詳細記憶の正答率（M = {M_low:.2f}, SD = {SD_low:.2f}）は，高情動強度条件（M = {M_high:.2f}, SD = {SD_high:.2f}）と比較して有意に{差の方向}であった（paired t({df}) = {t:.2f}, p = {p:.3f}, Cohen's d = {d:.2f}）。」

- 例（混合 ANOVA の記述）:
	- 「混合 ANOVA によれば，情動強度の主効果が有意であった（F({df1},{df2}) = {F:.2f}, p = {p:.3f}, partial η² = {eta2:.3f}）。告知条件の主効果は{有意/非有意}であり，強度と告知の交互作用は{有意/非有意}であった（F({df1},{df2}) = {Fint:.2f}, p = {pint:.3f}, partial η² = {eta2int:.3f}）。」

注: 上記テンプレート中の括弧内 `{...}` は解析結果で置換できるプレースホルダです。

3) 図の要件
- 棒グラフまたは折れ線グラフ（論文用）を1枚作成する:
	- X 軸: `intensity`（`low` / `high`）
	- Y 軸: `accuracy`
	- 色または線種で `expectancy`（告知/未告知） を区別（例: 青 = 未告知, 赤 = 告知）
	- エラーバーは標準誤差または 95% 信頼区間を表示
	- 図は高解像度で保存（例: PNG/TIFF, dpi ≥ 300）

6. 実装ノート（補助）
- 欠損値がある被験者は対応 t 検定のペアから除外するか，欠損値処理のルールを明確にする。
- Cohen's d の計算は被験者内効果量（paired d）として，差スコアの平均を差スコアの標準偏差で割る方法が一般的です。
- 混合 ANOVA で部分 η² を取得するには `pingouin` の出力を利用するか，`statsmodels` で手計算する場合は分散成分を計算して算出します。

7. 次のアクション
- あなたが `item_id`→`intensity` のマッピング表を提供してくだされば，データ整形（`intensity` 付与・集約）と，
	- (A) 対応 t 検定の実行・結果出力（t, df, p, d, M, SD）
	- (B) 混合 ANOVA の実行・結果出力（F, df, p, partial η²）
	- (C) 論文用の図（高解像度 PNG）作成
	を自動で実行する Python スクリプトを作成して実行します。

---

この翻訳の内容でスクリプト化（実コードの作成）をご希望であれば、マッピング表を添付して指示してください。必要に応じて `pingouin` を使う例か `statsmodels` を使う例、どちらが良いかも指定してください。