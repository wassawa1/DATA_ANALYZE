import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

base = Path(__file__).resolve().parent.parent
out = base / 'analyze' / 'outputs'
# paths
cleaned = out / 'data_cleaned.csv'
agg = out / 'aggregated_accuracy_long.csv'
paired = out / 'analysisA_paired_t_results.csv'

print('Files exist: cleaned={}, agg={}, paired={}'.format(cleaned.exists(), agg.exists(), paired.exists()))

df = pd.read_csv(cleaned) if cleaned.exists() else pd.DataFrame()
agg_long = pd.read_csv(agg) if agg.exists() else pd.DataFrame()
paired_wide = pd.read_csv(paired) if paired.exists() else pd.DataFrame()

print('\n== データ概要 ==')
if not df.empty:
    print('長形式データ行数:', len(df))
    if 'item_id' in df.columns:
        print('item_id unique count:', df['item_id'].nunique())
    print("memory_type values:", df['memory_type'].value_counts(dropna=False).to_dict() if 'memory_type' in df.columns else 'no col')
    if 'correct' in df.columns:
        print('correct unique values (sample):', sorted(df['correct'].dropna().unique())[:20])
    if 'expectancy' in df.columns:
        print('expectancy value counts:', df['expectancy'].value_counts(dropna=False).to_dict())
    if 'intensity' in df.columns:
        print('intensity value counts:', df['intensity'].value_counts(dropna=False).to_dict())

print('\n== 集計 (agg_long) 概要 ==')
if not agg_long.empty:
    print('agg_long rows:', len(agg_long))
    try:
        print(agg_long.groupby(['intensity'])['accuracy'].agg(['count','mean','std']).to_string())
    except Exception as e:
        print('agg_long 集計エラー:', e)

print('\n== paired wide (保存されたもの) ==')
if not paired_wide.empty:
    print('paired_wide shape:', paired_wide.shape)
    print('columns:', paired_wide.columns.tolist()[:10])

print('\n== 再計算: 被験者ごとの low/high 平均 (verbatim) ==')
if not df.empty:
    d = df.copy()
    if 'memory_type' in d.columns:
        d = d[d['memory_type']=='verbatim']
    # ensure intensity exists
    if 'intensity' not in d.columns:
        print('intensity 列がありません — マップの結合が必要')
    else:
        counts = d.dropna(subset=['item_id','intensity']).groupby(['subject_id','intensity']).size().unstack(fill_value=0)
        print('被験者×強度の項目数の統計:')
        print(counts.describe().to_string())
        acc = (
            d.dropna(subset=['correct','intensity'])
             .groupby(['subject_id','intensity'])['correct'].mean()
             .unstack()
        )
        print('acc cols:', acc.columns.tolist())
        if 'low' in acc.columns and 'high' in acc.columns:
            paired = acc.dropna(subset=['low','high']).copy()
            diffs = paired['low'] - paired['high']
            print('再計算でのペア数 =', len(diffs))
            print('mean low, high:', paired['low'].mean(), paired['high'].mean())
            if len(diffs) >= 3:
                sh = stats.shapiro(diffs)
                print('Shapiro-Wilk on diffs: W={:.4f}, p={:.4f}'.format(sh.statistic, sh.pvalue))
            else:
                print('Shapiro の検定に十分なサンプルがありません')
            if len(diffs) >= 1:
                try:
                    wil = stats.wilcoxon(paired['low'], paired['high'])
                    print('Wilcoxon signed-rank: statistic={}, p={}'.format(wil.statistic, wil.pvalue))
                except Exception as e:
                    print('Wilcoxon error:', e)
        else:
            print('low/high 列が揃っていません:', acc.columns.tolist())

print('\n== 注意点チェック ==')
if not df.empty and 'correct' in df.columns:
    sample_vals = df['correct'].dropna().unique()
    print('correct unique (count):', len(sample_vals), 'examples:', sorted(sample_vals)[:20])
    if set(np.unique(df['correct'].dropna())).issubset({0,1}):
        print('correct は 0/1 の二値に見えます。')
    else:
        print('correct が 0/1 でない値を含みます。スコアの扱いを確認してください。')

print('\n検査完了')
