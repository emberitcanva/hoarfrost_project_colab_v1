"""Validation checks for model inputs and outputs."""

from __future__ import annotations

import math
from typing import Iterable

import pandas as pd


def check_required_columns(df: pd.DataFrame, required: Iterable[str], df_name: str = "DataFrame") -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} is missing required columns: {missing}")


def check_no_nan(df: pd.DataFrame, columns: Iterable[str], df_name: str = "DataFrame") -> None:
    bad = [col for col in columns if df[col].isna().any()]
    if bad:
        raise ValueError(f"{df_name} contains NaN in required columns: {bad}")


def check_non_negative_hoarfrost_state(df: pd.DataFrame) -> None:
    for col in ["H_m", "rho_t_kg_per_m3", "mass_per_m_kg_per_m"]:
        if col in df.columns and (pd.to_numeric(df[col], errors="coerce") < 0.0).any():
            raise ValueError(f"Negative values found in {col}")


def check_reset_conditions(df: pd.DataFrame) -> None:
    required = ["ta_C", "T1_C", "was_reset", "H_m", "rho_t_kg_per_m3", "mass_per_m_kg_per_m"]
    check_required_columns(df, required, "simulation output")
    mask = (pd.to_numeric(df["ta_C"], errors="coerce") > 0.0) | (pd.to_numeric(df["T1_C"], errors="coerce") > 0.0)
    if not ((df.loc[mask, "was_reset"] == True).all()):  # noqa: E712
        raise ValueError("Rows with ta_C > 0 or T1_C > 0 must have was_reset=True")
    for col in ["H_m", "rho_t_kg_per_m3", "mass_per_m_kg_per_m"]:
        if not (pd.to_numeric(df.loc[mask, col], errors="coerce").fillna(0.0) == 0.0).all():
            raise ValueError(f"Rows after reset must have {col}=0")


def check_finite_numeric(value: float, name: str) -> None:
    if not math.isfinite(float(value)):
        raise ValueError(f"{name} must be finite")


def run_basic_output_checks(df: pd.DataFrame) -> None:
    check_required_columns(
        df,
        ["timestamp", "ta_C", "T1_C", "H_m", "rho_t_kg_per_m3", "mass_per_m_kg_per_m", "was_reset"],
        "simulation output",
    )
    check_non_negative_hoarfrost_state(df)
    check_reset_conditions(df)

