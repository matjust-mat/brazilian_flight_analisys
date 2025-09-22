import argparse
from pathlib import Path
import pandas as pd

def drop_column_if_too_many_invalid(df: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    """
    Drop columns whose proportion of valid entries is below `threshold`.

    A cell is considered *invalid* if it is:
      - missing (NaN/NA), or
      - an empty string after trim, or
      - a case-insensitive text placeholder: {"null", "nan", "none"}.

    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    threshold : float, default 0.05
        Minimum fraction of valid entries required to keep a column.
        Range is [0, 1]. For example, 0.05 keeps columns with >=5% valid data.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with low-validity columns removed. The input `df` is not modified.
    """
    na_mask = df.isna()

    s = df.astype("string").apply(lambda col: col.str.strip())

    placeholder = {"null", "nan", "none"}
    s_lower = s.apply(lambda col: col.str.casefold())
    placeholder_mask = s_lower.isin(placeholder)

    empty_mask = s.eq("")

    invalid_mask = na_mask | empty_mask | placeholder_mask

    valid_ratio = 1.0 - invalid_mask.mean(axis=0)

    to_drop = valid_ratio[valid_ratio < threshold].index.tolist()
    print(f"Dropping {len(to_drop)} columns with <{threshold*100:.1f}% valid data: {to_drop}")
    return df.drop(columns=to_drop)

def main():
    parser = argparse.ArgumentParser(description="Filtering airport codes from Brazil (BR).")
    parser.add_argument("--input", type=Path, default=Path("./data/flat-ui__data-Sun Sep 21 2025.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("./sanitized_data"))
    parser.add_argument("--outfile", type=str, default="sanitized_airpot_codes.csv")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    outpath = args.outdir / args.outfile

    err = None
    df = None
    try:
        df = pd.read_csv(args.input, sep=",", keep_default_na=True, na_values="null")
    except Exception as e:
        err = e
        df = None

    if df is None and err is not None:
        raise RuntimeError(f"Failed to read input file. Error: {err}")

    if "iso_country" not in df.columns:
        raise RuntimeError(f"Could not find 'iso_country' column. Columns available: {list(df.columns)}")

    country_col = "iso_country"
    df[country_col] = df[country_col].astype(str).str.strip().str.upper()
    filtered = df[df[country_col] == "BR"].copy()

    filtered = drop_column_if_too_many_invalid(filtered)

    filtered.to_csv(outpath, index=False, sep=';')

    print(f"Wrote {len(filtered)} rows to {outpath}")
    print(f"Columns: {list(filtered.columns)}")

if __name__ == "__main__":
    main()
