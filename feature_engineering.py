#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delay Feature Engineering and Aggregations
- Reads the standardized CSV (vra_clean_base.csv)
- Creates date and delay features
- Generates aggregation CSVs for analysis
"""

import argparse, os
import numpy as np
import pandas as pd

DATE_FORMATS = ["%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"]
WEEKDAY_PT = {0:"segunda",1:"terca",2:"quarta",3:"quinta",4:"sexta",5:"sabado",6:"domingo"}

def parse_datetime(series: pd.Series) -> pd.Series:
    """
    Parses a pandas Series of date/time strings into datetime objects using multiple possible formats.
    Attempts to convert each string in the input Series to a pandas datetime object by trying a list of predefined formats.
    If parsing fails for a format, it tries the next one in the list. If all formats fail, it falls back to a generic parsing
    attempt with day-first interpretation.
    Args:
        series (pd.Series): A pandas Series containing date/time strings to be parsed.
    Returns:
        pd.Series: A pandas Series of parsed datetime objects (dtype: datetime64[ns]), with NaT for unparseable entries.
    Note:
        Requires the global variable DATE_FORMATS to be defined as a list of date/time format strings.
    """
    s = series.astype("string").str.strip()
    dt = pd.to_datetime(s, format=DATE_FORMATS[0], errors="coerce")
    for fmt in DATE_FORMATS[1:]:
        dt = dt.fillna(pd.to_datetime(s, format=fmt, errors="coerce"))
    dt = dt.fillna(pd.to_datetime(s, errors="coerce", dayfirst=True, utc=False))
    return dt

def minutes_diff(late: pd.Series, early: pd.Series) -> pd.Series:
    """
    Calculates the difference in minutes between two pandas Series of datetime values.
    Args:
        late (pd.Series): Series of later datetime values.
        early (pd.Series): Series of earlier datetime values.
    Returns:
        pd.Series: Series containing the difference in minutes between corresponding elements of `late` and `early`.
    """
    return (late - early).dt.total_seconds().div(60)

def bucket_hour(h):
    """
    Categorizes an hour into a time-of-day bucket.
    Parameters:
        h (int or float or pandas.NA): The hour to categorize. Can be an integer (0-23), float, or pandas.NA.
    Returns:
        str or pandas.NA: Returns one of the following strings based on the hour:
            - "manha" for hours between 5 (inclusive) and 12 (exclusive)
            - "tarde" for hours between 12 (inclusive) and 18 (exclusive)
            - "noite" for hours between 18 (inclusive) and 24 (exclusive)
            - "madrugada" for hours between 0 (inclusive) and 5 (exclusive)
            - pandas.NA if the input is pandas.NA
    Raises:
        ValueError: If the input hour is not in the range 0-23 (inclusive).
    Note:
        This function assumes that the input hour is in a 24-hour format.
    """
    if pd.isna(h): return pd.NA
    h = int(h)
    if 5 <= h < 12: return "manha"
    if 12 <= h < 18: return "tarde"
    if 18 <= h < 24: return "noite"
    return "madrugada"

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enhances a flight DataFrame with engineered features for analysis.
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing flight data. Expected columns include:
        - 'dep_scheduled', 'dep_actual', 'arr_scheduled', 'arr_actual' (datetime or string)
        - 'airline_icao', 'origin_icao', 'dest_icao' (string)
        - 'flight_status' (string)
    Returns
    -------
    pd.DataFrame
        DataFrame with additional engineered features:
        - Parsed and standardized datetime columns.
        - Standardized ICAO code columns.
        - 'dep_delay_min', 'arr_delay_min': Departure and arrival delays in minutes.
        - 'status_norm': Normalized flight status.
        - 'atraso': Boolean flag for significant delay (>= 30 min).
        - 'year', 'month', 'weekday_num', 'weekday', 'hour': Temporal features.
        - 'periodo_dia': Time-of-day bucket.
        - 'route_icao': Route identifier (origin-destination).
        - 'year_month': Year and month string (YYYY-MM).
    """
    for c in ("dep_scheduled","dep_actual","arr_scheduled","arr_actual"):
        if c in df.columns:
            df[c] = parse_datetime(df[c])
        else:
            df[c] = pd.NaT

    for c in ("airline_icao","origin_icao","dest_icao"):
        if c in df.columns:
            df[c] = df[c].astype("string").str.upper().str.strip()

    df["dep_delay_min"] = minutes_diff(df["dep_actual"], df["dep_scheduled"])
    df["arr_delay_min"] = minutes_diff(df["arr_actual"], df["arr_scheduled"])

    s = df.get("flight_status", pd.Series(index=df.index, dtype="string")).astype("string").str.upper().str.strip()
    df["status_norm"] = np.select(
        [s.str.contains("CANCEL", na=False), s.str.contains("REALIZ", na=False), s.str.contains("NÃO INFORM", na=False) | s.str.contains("NAO INFORM", na=False)],
        ["CANCELADO","REALIZADO","NAO_INFORMADO"],
        default=s
    )

    df["atraso"] = (df["arr_delay_min"] >= 30) | ((df["arr_delay_min"].isna()) & (df["dep_delay_min"] >= 30))

    base_time = df["dep_scheduled"].fillna(df["arr_scheduled"])
    df["year"] = base_time.dt.year
    df["month"] = base_time.dt.month
    df["weekday_num"] = base_time.dt.weekday
    df["weekday"] = df["weekday_num"].map(WEEKDAY_PT)
    df["hour"] = base_time.dt.hour
    df["periodo_dia"] = df["hour"].apply(bucket_hour)
    df["route_icao"] = df.get("origin_icao", pd.Series(index=df.index, dtype="string")).fillna("").astype("string") + "-" + \
                       df.get("dest_icao", pd.Series(index=df.index, dtype="string")).fillna("").astype("string")
    df["year_month"] = df["year"].astype("Int64").astype("string") + "-" + df["month"].astype("Int64").astype("string").str.zfill(2)
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean_csv", required=True, help="Arquivo sanitizado (vra_clean_base.csv)")
    ap.add_argument("--out", required=True, help="Diretorio de saida para features")
    args = ap.parse_args()

    df = pd.read_csv(args.clean_csv, dtype=str)
    df = build_features(df)
    os.makedirs(args.out, exist_ok=True)
    df.to_csv(os.path.join(args.out, "vra_clean_with_features.csv"), index=False)
    print("OK")

if __name__ == "__main__":
    main()
