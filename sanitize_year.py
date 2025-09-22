#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sanitizacao ANAC VRA
- Le CSVs mensais brutos (ANAC VRA)
- Seleciona e renomeia 12 campos exigidos
- Corrige mojibake em cabecalhos
- Concatena todos os meses
- Salva em parquet compactado
"""

import argparse, glob, os, sys
from typing import Dict, List
import pandas as pd

TARGETS: Dict[str, str] = {
    "icao empresa aérea": "airline_icao",
    "número voo": "flight_number",
    "código autorização (di)": "auth_code_di",
    "código tipo linha": "line_type",
    "icao aeródromo origem": "origin_icao",
    "icao aeródromo destino": "dest_icao",
    "partida prevista": "dep_scheduled",
    "partida real": "dep_actual",
    "chegada prevista": "arr_scheduled",
    "chegada real": "arr_actual",
    "situação voo": "flight_status",
    "situação do voo": "flight_status",
    "código justificativa": "justification_code",
}

def _fix_mojibake(s: str) -> str:
    """
    Attempts to fix mojibake (garbled text) caused by incorrect encoding.
    Tries to re-encode the input string from 'latin1' and decode it as 'utf-8'.
    If the conversion fails, returns the original string unchanged.
    Args:
        s (str): The input string that may contain mojibake.
    Returns:
        str: The corrected string if conversion is successful, otherwise the original string.
    """
    try:
        return s.encode("latin1").decode("utf-8")
    except Exception:
        return s

def _canon(s: str) -> str:
    """
    Normalizes and cleans up a string by fixing encoding issues, trimming whitespace and quotes,
    removing BOM characters, converting to lowercase, and replacing specific known mojibake substrings
    with their correct forms.
    Args:
        s (str): The input string to be normalized.
    Returns:
        str: The cleaned and normalized string.
    """
    s = _fix_mojibake(s).strip().strip('"').replace("\ufeff","").lower()
    s = (s.replace("empresa aã©rea","empresa aérea")
           .replace("aerã³dromo","aeródromo"))
    s = " ".join(s.split())
    return s

ORDER = [
    "airline_icao","flight_number","auth_code_di","line_type",
    "origin_icao","dest_icao",
    "dep_scheduled","dep_actual","arr_scheduled","arr_actual",
    "flight_status","justification_code",
]

def sanitize_one(path: str) -> pd.DataFrame:
    """
    Sanitizes an ANAC VRA CSV file.
    Returns a DataFrame with renamed and selected columns.
    Raises ValueError if no target column is found.
    Raises FileNotFoundError if the file does not exist.
    Raises pd.errors.ParserError if the file cannot be read.
    12 target columns:
    - airline_icao
    - flight_number
    - auth_code_di
    - line_type
    - origin_icao
    - dest_icao
    - dep_scheduled
    - dep_actual
    - arr_scheduled
    - arr_actual
    - flight_status
    - justification_code

    1 additional column:
    - source_file: name of the source file

    13 columns in total.
    """
    df = pd.read_csv(path, sep=";", quotechar='"', encoding="latin1", dtype=str, skiprows=1, engine="python")
    rename_map = {}
    selected_src = []
    for col in df.columns:
        key = _canon(col)
        if key in TARGETS:
            rename_map[col] = TARGETS[key]
            selected_src.append(col)
    if not selected_src:
        raise ValueError(f"Nenhuma coluna-alvo encontrada em {path}.")
    df2 = df[selected_src].rename(columns=rename_map)
    df2 = df2[[c for c in ORDER if c in df2.columns]]
    df2["source_file"] = os.path.basename(path)
    return df2

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, help='Glob dos CSVs, ex: "/data/VRA_2002*.csv"')
    ap.add_argument("--out", required=True, help="Diretorio de saida")
    args = ap.parse_args()

    paths = sorted(glob.glob(args.inputs))
    if not paths:
        raise FileNotFoundError("Nenhum arquivo encontrado.")
    frames: List[pd.DataFrame] = []
    for p in paths:
        print(f"Processing {p}...")
        try:
            frames.append(sanitize_one(p))
        except Exception as e:
            print(f"[WARN] {p}: {e}", file=sys.stderr)
    if not frames:
        raise RuntimeError("Falha na sanitizacao de todos os arquivos.")
    out = pd.concat(frames, ignore_index=True)
    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "vra_clean_base.csv")
    out.to_csv(out_path, index=False)
    print(out_path)

if __name__ == "__main__":
    main()
