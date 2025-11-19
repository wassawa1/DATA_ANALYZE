# 設問番号からHAレベルを返す関数
def get_ha_level(idx):
    """
    設問番号 idx から HAレベル (1,2,3,4) を返す。
    データフレームの 'HAレベル' 列の値と一致するように設計。
    必要に応じて範囲を調整してください。
    """
    # 例: 1-37: 1, 38-62: 2, 63-92: 3, 93-134: 4
    if 1 <= idx <= 37:
        return 1
    elif 38 <= idx <= 62:
        return 2
    elif 63 <= idx <= 92:
        return 3
    elif 93 <= idx <= 134:
        return 4
    # 135以降は順序記憶なので None
    return None
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


# Low / High の対応表（ペアリスト） - 多くのスクリプトで共通利用するためこちらに移動しました。
LOW_HIGH_PAIRS = [
    (6, 31), (7, 30), (19, 21), (20, 34), (39, 77), (40, 66),
    (44, 92), (45, 69), (49, 79), (52, 84),
    ([53,54,55], [71,72,73,74,75,76]),
    (56, 63), (93, 128), (95, 127), (97, 121), (99, 134),
    (106, 124), (108, 131), (110, 132), (118, 123), (103, 125), (113, 130)
]


def expand_pairs(pairs):
    """Expand a list of low/high pairs where each element may be an int or list.

    Returns two sorted lists: (low_items, high_items).
    """
    low_items = []
    high_items = []
    for low, high in pairs:
        low_items.extend(low if isinstance(low, list) else [low])
        high_items.extend(high if isinstance(high, list) else [high])
    return sorted(low_items), sorted(high_items)


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
    """Resolve the data file path using this precedence (keeps file names unchanged):

    1. If environment variable `DATA_FILE` is set and points to an existing file, use it.
    2. If `filename` exists in the repository root, use it.
    3. If `filename` exists in `./data` or `./data/raw`, use it.
    4. If a single `.xlsx` file exists in `./data` or `./data/raw`, use that file.

    If multiple `.xlsx` files are found in a data directory, we raise so the user
    can explicitly set `DATA_FILE` (we do not guess among multiple candidates).
    """
    # 1) env var override
    env_path = os.environ.get("DATA_FILE")
    if env_path:
        env_path = os.path.abspath(env_path)
        if os.path.exists(env_path):
            return env_path
        else:
            raise FileNotFoundError(f"Environment variable DATA_FILE is set but file not found: {env_path}")

    # repository root (directory containing this file)
    repo_root = os.path.abspath(os.path.dirname(__file__))

    # 2) direct match in repo root
    candidate = os.path.join(repo_root, filename)
    if os.path.exists(candidate):
        return candidate

    # helper to search a directory: exact filename first, then single-xlsx fallback
    def _search_dir_for_file(directory: str):
        if not os.path.isdir(directory):
            return None
        exact = os.path.join(directory, filename)
        if os.path.exists(exact):
            return exact
        # gather .xlsx files (ignore temp/hidden files starting with ~)
        xlsx_files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.lower().endswith('.xlsx') and not f.startswith('~')
        ]
        if len(xlsx_files) == 1:
            return os.path.abspath(xlsx_files[0])
        return None

    # 3) search ./data and ./data/raw (same rules)
    data_dirs = [os.path.join(repo_root, 'data'), os.path.join(repo_root, 'data', 'raw')]
    for d in data_dirs:
        found = _search_dir_for_file(d)
        if found:
            return found

    # Nothing matched: construct helpful error message listing options
    tried = [
        ("env DATA_FILE", os.environ.get('DATA_FILE')),
        ("repo root", candidate),
    ]
    tried_dirs = '\n'.join([f" - {p}" for p in data_dirs])
    raise FileNotFoundError(
        f"Data file '{filename}' not found. Tried:\n"
        f" - Environment variable DATA_FILE: {os.environ.get('DATA_FILE')}\n"
        f" - Repository root: {candidate}\n"
        f" - Data directories (exact filename or single .xlsx fallback):\n{tried_dirs}\n\n"
        f"Please set the environment variable `DATA_FILE` to the exact file path,\n"
        f"or place a single .xlsx in one of the data directories, or put '{filename}' in the repo root."
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
