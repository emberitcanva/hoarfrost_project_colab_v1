"""Calibration and input preparation helpers.

This module prepares model inputs; it does not fit or alter physical formulas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.makkonen_model import saturation_vapor_pressure_ice_Pa


@dataclass
class CalibrationConfig:
    R_ohm_per_m: float
    default_pressure_Pa: float = 101325.0
    fill_missing_wind_with_zero: bool = True
    current_match_tolerance_s: int = 325


def actual_vapor_pressure_Pa(ta_C: float | pd.Series, rh_pct: float | pd.Series) -> float | pd.Series:
    """Confirmed decision D-01: ea over ice."""
    return (rh_pct / 100.0) * np.vectorize(saturation_vapor_pressure_ice_Pa)(ta_C)


def joule_heating_W_per_m(current_A: float | pd.Series, R_ohm_per_m: float) -> float | pd.Series:
    """Confirmed formula: QJ = I^2 * R'."""
    return current_A ** 2 * R_ohm_per_m


def estimate_calibration_state(
    df: pd.DataFrame,
    T_col: str = "T1_C",
    phi_H_col: str = "phi_H_deg",
    phi_K1_col: str = "phi_K1_deg",
    no_ice_mask: pd.Series | None = None,
) -> dict[str, Any]:
    """Estimate calibration state as medians over no-ice rows.

    If no_ice_mask is not supplied, rows with T1_C > 0 are used. This mirrors
    the confirmed reset/no-ice decision and remains a calibration heuristic.
    """
    if no_ice_mask is None:
        no_ice_mask = pd.to_numeric(df[T_col], errors="coerce") > 0.0
    ref = df.loc[no_ice_mask, [T_col, phi_H_col, phi_K1_col]].dropna()
    if ref.empty:
        return {"quality": "no_reference_rows", "T_cal_C": None, "phi_H_cal_deg": None, "phi_K1_cal_deg": None}
    return {
        "quality": "ok",
        "n_reference_rows": int(len(ref)),
        "T_cal_C": float(pd.to_numeric(ref[T_col], errors="coerce").median()),
        "phi_H_cal_deg": float(pd.to_numeric(ref[phi_H_col], errors="coerce").median()),
        "phi_K1_cal_deg": float(pd.to_numeric(ref[phi_K1_col], errors="coerce").median()),
    }


def build_calibrated_dataset(df: pd.DataFrame, config: CalibrationConfig) -> pd.DataFrame:
    """Build the minimal DataFrame consumed by simulation_runner.

    Expected input columns:
    timestamp, ta_C, T1_C, rh_pct, pa_Pa, v_m_per_s, n_tenths,
    qS_W_per_m2, current_A, delta_tau_s, phi_H_deg, phi_K1_deg.
    """
    required = [
        "timestamp",
        "ta_C",
        "T1_C",
        "rh_pct",
        "pa_Pa",
        "v_m_per_s",
        "n_tenths",
        "qS_W_per_m2",
        "current_A",
        "delta_tau_s",
        "phi_H_deg",
        "phi_K1_deg",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"build_calibrated_dataset: missing columns {missing}")
    out = df.copy()
    numeric_cols = [col for col in required if col != "timestamp"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["pa_Pa"] = out["pa_Pa"].fillna(config.default_pressure_Pa)
    if config.fill_missing_wind_with_zero:
        out["v_m_per_s"] = out["v_m_per_s"].fillna(0.0)
    out["ea_Pa"] = actual_vapor_pressure_Pa(out["ta_C"], out["rh_pct"])
    out["QJ_W_per_m"] = joule_heating_W_per_m(out["current_A"], config.R_ohm_per_m)
    return out[
        [
            "timestamp",
            "ta_C",
            "T1_C",
            "ea_Pa",
            "pa_Pa",
            "v_m_per_s",
            "n_tenths",
            "qS_W_per_m2",
            "QJ_W_per_m",
            "delta_tau_s",
            "phi_H_deg",
            "phi_K1_deg",
            "rh_pct",
            "current_A",
        ]
    ].sort_values("timestamp").reset_index(drop=True)


def compute_qS_with_pvlib(*args, **kwargs):
    """Optional qS helper.

    pvlib was explicitly allowed by decision D-02, but project data and exact
    solar calculation settings are site/workflow-specific. This function is a
    guarded hook rather than a hidden formula.
    """
    try:
        import pvlib  # noqa: F401
    except ImportError as exc:
        raise ImportError("pvlib is not installed. Install it in Colab with `pip install pvlib`.") from exc
    raise NotImplementedError("REQUIRES_USER_DECISION: pass site/time-specific pvlib implementation here.")

