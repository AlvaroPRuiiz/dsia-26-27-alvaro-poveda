"""Pipeline de ejemplo: ventas CSV → limpieza → métricas JSON.

Sesión 5 oct 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "fecha",
    "region",
    "producto",
    "unidades",
    "precio_unitario",
    "cliente_id",
}


def setup_logging(log_file: Path | None = None) -> logging.Logger:
    logger = logging.getLogger("pipeline_ventas")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    logger.addHandler(stream)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    return logger


def load(path: Path, logger: logging.Logger) -> pd.DataFrame:
    logger.info("Cargando %s", path)
    if not path.exists():
        logger.error("No existe el fichero de entrada: %s", path)
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        logger.error("Faltan columnas requeridas: %s", sorted(missing))
        raise ValueError(f"missing columns: {sorted(missing)}")
    return frame


def transform(frame: pd.DataFrame, logger: logging.Logger | None = None) -> tuple[pd.DataFrame, dict]:
    work = frame.copy()
    work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
    work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")
    ok = work["unidades"].notna() & (work["unidades"] > 0) & (work["precio_unitario"] > 0)
    clean = work.loc[ok].copy()
    clean["importe"] = clean["unidades"] * clean["precio_unitario"]
    report = {
        "rows_in": int(len(work)),
        "rows_out": int(len(clean)),
        "rows_dropped": int((~ok).sum()),
        "importe_total": float(clean["importe"].sum()) if len(clean) else 0.0,
        "error_rate": float((~ok).sum() / len(work)) if len(work) else 0.0,
    }
    if logger:
        logger.info("Transformación: %s", report)
    return clean, report


def save(clean: pd.DataFrame, report: dict, out_dir: Path, logger: logging.Logger) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_path = out_dir / "ventas_limpias.csv"
    report_path = out_dir / "metrics.json"
    clean.to_csv(clean_path, index=False)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Escrito %s y %s", clean_path, report_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline de ventas")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--max-error-rate",
        type=float,
        default=0.5,
        help="Abortar si rows_dropped/rows_in supera este umbral",
    )
    args = parser.parse_args(argv)

    logger = setup_logging(args.output_dir / "run.log")
    try:
        frame = load(args.input, logger)
    except (FileNotFoundError, ValueError):
        return 2

    clean, report = transform(frame, logger)
    if report["error_rate"] > args.max_error_rate:
        logger.error(
            "error_rate %.3f > max-error-rate %.3f — abortando",
            report["error_rate"],
            args.max_error_rate,
        )
        return 1

    save(clean, report, args.output_dir, logger)
    return 0


if __name__ == "__main__":
    sys.exit(main())
