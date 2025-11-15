import os
import pandas as pd
import matplotlib

# フォント設定（日本語・中国語対応）
matplotlib.rcParams["font.family"] = "Microsoft YaHei"
matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei", "SimHei", "SimSun", "MS Gothic"
]
matplotlib.rcParams["axes.unicode_minus"] = False

# フォントサイズの共通設定
# ベースフォントサイズを上げて読みやすくする
BASE_FONT_SIZE = 14
LEGEND_FONT_SIZE = 12
ANNOTATION_FONT_SIZE = 12

matplotlib.rcParams['font.size'] = BASE_FONT_SIZE
matplotlib.rcParams['axes.titlesize'] = BASE_FONT_SIZE
matplotlib.rcParams['axes.labelsize'] = BASE_FONT_SIZE
matplotlib.rcParams['xtick.labelsize'] = BASE_FONT_SIZE - 2
matplotlib.rcParams['ytick.labelsize'] = BASE_FONT_SIZE - 2
matplotlib.rcParams['legend.fontsize'] = LEGEND_FONT_SIZE


def normalize_score_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Excel にある「点数」列を '点数1', '点数2', ... に正規化して float に変換する。

    例: "1.00 / 1" -> 1.0
    """
    rename_map = {
        col: f"点数{i+1}"
        for i, col in enumerate(df.filter(regex=r"^点数(\.\d+)?$").columns)
    }
    df = df.rename(columns=rename_map)

    for col in df.filter(regex=r"^点数\d+$").columns:
        df[col] = df[col].str.split("/").str[0].str.strip().astype(float)

    return df


# 映画×高低の 6 区間定義（多くのスクリプトで共通利用）
groups = [
    (1, 20,  "映画1_低", "red"),
    (21, 37, "映画1_高", "blue"),
    (38, 62, "映画2_低", "red"),
    (63, 92, "映画2_高", "blue"),
    (93,118, "映画3_低", "red"),
    (119,134,"映画3_高", "blue"),
]


def load_sheet(path: str, sheet_name: str) -> pd.DataFrame:
    """Excel シートを読み込み、点数列を正規化して返す。"""
    df = pd.read_excel(path, sheet_name=sheet_name)
    return normalize_score_columns(df)


# データ配置・出力ディレクトリのデフォルト
DATA_DIR = os.path.join("data", "raw")
OUTPUT_DIR = "outputs"


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def data_file_path(filename: str) -> str:
    """`data/raw/` 配下のファイルパスを返す。ディレクトリが無ければ作成しない（ユーザーが元データを置く想定）。"""
    return os.path.join(DATA_DIR, filename)


def output_file_path(filename: str) -> str:
    """`outputs/` 配下のファイルパスを返し、出力ディレクトリを作成する。"""
    ensure_dir(OUTPUT_DIR)
    return os.path.join(OUTPUT_DIR, filename)


def ensure_data_dir():
    """`data/raw/` ディレクトリを作成する（元データを置くためのフォルダ）。"""
    ensure_dir(DATA_DIR)
