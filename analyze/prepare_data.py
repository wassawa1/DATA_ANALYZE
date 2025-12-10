import sys
from pathlib import Path
import pandas as pd
import numpy as np


def find_input(base: Path):
    # 候補ファイル名の順で探す
    candidates = [
        "データ_edit.xlsx",
        "データ_edit.xlsx",
        "data_edit.xlsx",
        "データ_edit.xls",
    ]
    data_dir = base.parent / "data"
    for name in candidates:
        p = data_dir / name
        if p.exists():
            return p
    # 代替: ディレクトリ内の xlsx を探す
    for p in data_dir.iterdir():
        if p.suffix.lower() in (".xlsx", ".xls") and not p.name.startswith("~$"):
            return p
    return None


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    # 小文字化して標準名を用意
    col_map = {}
    lowcols = {c.lower(): c for c in df.columns}
    if "subject_id" in lowcols:
        col_map[lowcols["subject_id"]] = "subject_id"
    if "item_id" in lowcols:
        col_map[lowcols["item_id"]] = "item_id"
    if "correct" in lowcols:
        col_map[lowcols["correct"]] = "correct"
    if "expectancy" in lowcols:
        col_map[lowcols["expectancy"]] = "expectancy"

    # 一般的な代替名にも対応
    for k, v in list(lowcols.items()):
        if k in ("subj", "id", "subject") and "subject_id" not in col_map.values():
            col_map[v] = "subject_id"
        if k in ("item", "itemid") and "item_id" not in col_map.values():
            col_map[v] = "item_id"
        if k in ("acc", "accuracy", "correctness") and "correct" not in col_map.values():
            col_map[v] = "correct"
        if k in ("expectancy", "expectation", "exp") and "expectancy" not in col_map.values():
            col_map[v] = "expectancy"

    df = df.rename(columns=col_map)
    return df


def main():
    base = Path(__file__).resolve().parent
    inp = find_input(base)
    if inp is None:
        print("入力ファイルが data フォルダに見つかりません。", file=sys.stderr)
        return 1

    print(f"入力ファイル: {inp}")
    try:
        df = pd.read_excel(inp)
    except Exception as e:
        print(f"Excel 読み込みエラー: {e}", file=sys.stderr)
        return 1

    df = normalize_columns(df)

    required = ["subject_id", "item_id", "correct", "expectancy"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"必須列が見つかりません: {missing}", file=sys.stderr)
        print("現在の列:", df.columns.tolist())
        return 1

    # 型変換
    df["item_id"] = pd.to_numeric(df["item_id"], errors="coerce")
    df["correct"] = pd.to_numeric(df["correct"], errors="coerce")
    df["expectancy"] = pd.to_numeric(df["expectancy"], errors="coerce")

    # memory_type を作成
    df["memory_type"] = np.where(df["item_id"].between(1, 134), "verbatim",
                                  np.where(df["item_id"].between(135, 206), "order", np.nan))

    # 削除や補正: correct は 0/1 にする
    df["correct"] = df["correct"].apply(lambda x: 1 if x == 1 else (0 if x == 0 else np.nan))

    # 集約: 被験者 × memory_type × expectancy ごとの accuracy
    agg = (
        df
        .dropna(subset=["subject_id", "memory_type", "expectancy", "correct"]) 
        .groupby(["subject_id", "memory_type", "expectancy"], as_index=False)["correct"].mean()
        .rename(columns={"correct": "accuracy"})
    )

    out_dir = base.parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "data_edit2.xlsx"

    try:
        with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="cleaned", index=False)
            agg.to_excel(writer, sheet_name="aggregated", index=False)
        print(f"出力しました: {out_file}")
        print("cleaned シート 行列:", df.shape)
        print("aggregated シート 行列:", agg.shape)
    except Exception as e:
        print(f"出力エラー: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
