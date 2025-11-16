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
ANNOTATION_FONT_SIZE = 8

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
    """Resolve the data file path using this precedence (do NOT read from data/raw by default):

    1. If environment variable `DATA_FILE` is set and points to an existing file, use it.
    2. If the requested filename exists in the repository root (same folder as this file's parent), use it.
    3. Otherwise raise FileNotFoundError with a helpful message.

    This avoids silently using `data/raw/` and respects the user's request not to rename/copy files.
    """
    # 1) env var override
    env_path = os.environ.get("DATA_FILE")
    if env_path:
        env_path = os.path.abspath(env_path)
        if os.path.exists(env_path):
            return env_path
        else:
            raise FileNotFoundError(f"Environment variable DATA_FILE is set but file not found: {env_path}")

    # 2) check repository root (assume this file is in repo root or a child)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    candidate = os.path.join(repo_root, filename)
    if os.path.exists(candidate):
        return candidate

    # Not found: raise so caller can abort with clear instruction
    raise FileNotFoundError(
        f"Data file '{filename}' not found. Set the environment variable DATA_FILE to the path of your Excel file,\n"
        f"or place '{filename}' in the repository root ({repo_root}).\n"
        f"Note: this function will NOT automatically read from data/raw or rename files."
    )


def output_file_path(filename: str) -> str:
    """`outputs/` 配下のファイルパスを返し、出力ディレクトリを作成する。"""
    ensure_dir(OUTPUT_DIR)
    return os.path.join(OUTPUT_DIR, filename)


def ensure_data_dir():
    """`data/raw/` ディレクトリを作成する（元データを置くためのフォルダ）。"""
    ensure_dir(DATA_DIR)


# Default output image settings to ensure consistent physical size
OUTPUT_DPI = 300
# default figure size in inches (width, height). Can be overridden per-figure.
OUTPUT_FIGSIZE = (14, 12)


def save_figure(fig, filename: str, figsize: tuple = None, dpi: int = None):
    """Save a Matplotlib figure using project defaults to ensure consistent image size.

    - `filename` is a basename saved under `outputs/`.
    - If `figsize` or `dpi` are not provided, `OUTPUT_FIGSIZE`/`OUTPUT_DPI` are used.
    - This does not use `bbox_inches='tight'` so pixel dimensions remain consistent.
    """
    if figsize is None:
        figsize = OUTPUT_FIGSIZE
    if dpi is None:
        dpi = OUTPUT_DPI

    fig.set_size_inches(figsize)
    out_path = output_file_path(filename)
    fig.savefig(out_path, dpi=dpi)
