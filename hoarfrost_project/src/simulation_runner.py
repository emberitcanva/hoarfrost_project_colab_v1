"""Simulation orchestration for Makkonen + Goryachev."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.common_types import CablePhysicalParams, GoryachevCalibrationParams, HoarfrostState, MeteoInput
from src.coupling_layer import compare_thickness_at_time, run_goryachev_diagnostic
from src.makkonen_model import update_hoarfrost_state
from src.validation_checks import run_basic_output_checks


def row_to_meteo_input(row: pd.Series) -> MeteoInput:
    return MeteoInput(
        ta_C=float(row["ta_C"]),
        T1_C=float(row["T1_C"]),
        ea_Pa=float(row["ea_Pa"]),
        pa_Pa=float(row["pa_Pa"]),
        v_m_per_s=float(row["v_m_per_s"]),
        n_tenths=float(row["n_tenths"]),
        qS_W_per_m2=float(row["qS_W_per_m2"]),
        QJ_W_per_m=float(row["QJ_W_per_m"]),
        delta_tau_s=float(row["delta_tau_s"]),
        prev_delta_T_c_K=float(row.get("prev_delta_T_c_K", 0.0)),
    )


def _flatten_section_diagnostics(row: dict[str, Any], diagnostics: dict[str, Any]) -> None:
    for section_name, section in diagnostics.get("section_results", {}).items():
        prefix = f"{section_name}_"
        for key, value in section.items():
            row[prefix + key] = value


def run_makkonen_timeseries(
    df_calibrated: pd.DataFrame,
    cable: CablePhysicalParams,
    initial_state: HoarfrostState | None = None,
    validate_output: bool = True,
) -> pd.DataFrame:
    """Run Makkonen state update over a calibrated time series."""
    state = initial_state if initial_state is not None else HoarfrostState()
    rows: list[dict[str, Any]] = []
    for _, input_row in df_calibrated.sort_values("timestamp").iterrows():
        meteo = row_to_meteo_input(input_row)
        result = update_hoarfrost_state(state, meteo, cable)
        state = result["state"]
        diagnostics = result.get("diagnostics", {})
        out = {
            "timestamp": input_row["timestamp"],
            "ta_C": meteo.ta_C,
            "T1_C": meteo.T1_C,
            "ea_Pa": meteo.ea_Pa,
            "pa_Pa": meteo.pa_Pa,
            "v_m_per_s": meteo.v_m_per_s,
            "n_tenths": meteo.n_tenths,
            "qS_W_per_m2": meteo.qS_W_per_m2,
            "QJ_W_per_m": meteo.QJ_W_per_m,
            "delta_tau_s": meteo.delta_tau_s,
            "H_m": state.H_m,
            "rho_t_kg_per_m3": state.rho_t_kg_per_m3,
            "mass_per_m_kg_per_m": state.mass_per_m_kg_per_m,
            "prev_delta_T_c_K": state.prev_delta_T_c_K,
            "Tc_prev_C": state.Tc_prev_C,
            "T1_prev_C": state.T1_prev_C,
            "was_reset": bool(result.get("was_reset", False)),
        }
        for key, value in diagnostics.items():
            if key != "section_results":
                out[key] = value
        _flatten_section_diagnostics(out, diagnostics)
        for optional_col in ["phi_H_deg", "phi_K1_deg"]:
            if optional_col in input_row:
                out[optional_col] = input_row[optional_col]
        rows.append(out)
    df_out = pd.DataFrame(rows)
    if validate_output:
        run_basic_output_checks(df_out)
    return df_out


def run_goryachev_diagnostic_at_t_star(
    df_simulated: pd.DataFrame,
    cable: CablePhysicalParams,
    calibration: GoryachevCalibrationParams,
    t_star,
) -> dict[str, Any]:
    """Run diagnostic comparison at an explicitly supplied timestamp t*."""
    df = df_simulated.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    t_star_dt = pd.to_datetime(t_star)
    matches = df.loc[df["timestamp"] == t_star_dt]
    if matches.empty:
        raise ValueError(f"t_star {t_star} not found in simulated DataFrame")
    row = matches.iloc[0]
    hoarfrost = HoarfrostState(
        H_m=float(row["H_m"]),
        rho_t_kg_per_m3=float(row["rho_t_kg_per_m3"]),
        mass_per_m_kg_per_m=float(row["mass_per_m_kg_per_m"]),
        prev_delta_T_c_K=float(row.get("prev_delta_T_c_K", 0.0)),
        Tc_prev_C=float(row["Tc_prev_C"]) if pd.notna(row.get("Tc_prev_C")) else None,
        T1_prev_C=float(row["T1_prev_C"]) if pd.notna(row.get("T1_prev_C")) else None,
    )
    mechanical = run_goryachev_diagnostic(
        hoarfrost=hoarfrost,
        cable=cable,
        calibration=calibration,
        T1_C=float(row["T1_C"]),
        phi_H_deg=float(row["phi_H_deg"]),
        phi_K1_deg=float(row["phi_K1_deg"]),
    )
    comparison = None
    if mechanical.status == "ok" and mechanical.c_m is not None:
        comparison = compare_thickness_at_time(hoarfrost.H_m, mechanical.c_m)
    return {
        "t_star": t_star_dt,
        "mechanical": mechanical,
        "comparison": comparison,
    }


def run_full_pipeline(
    df_calibrated: pd.DataFrame,
    cable: CablePhysicalParams,
    calibration: GoryachevCalibrationParams | None = None,
    t_star=None,
    initial_state: HoarfrostState | None = None,
) -> dict[str, Any]:
    """Run Makkonen over all rows and optional Goryachev diagnostic at t*."""
    df_sim = run_makkonen_timeseries(df_calibrated, cable, initial_state=initial_state)
    diagnostic = None
    if calibration is not None and t_star is not None:
        diagnostic = run_goryachev_diagnostic_at_t_star(df_sim, cable, calibration, t_star)
    return {"simulation": df_sim, "goryachev_diagnostic": diagnostic}

