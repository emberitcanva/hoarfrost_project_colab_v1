"""Basic smoke tests for imports and formula execution."""

from __future__ import annotations

import pandas as pd

from config.constants import case_01_cable_params, case_01_initial_hoarfrost_state
from src.calibration import CalibrationConfig, build_calibrated_dataset
from src.goryachev_model import alpha_star_1_per_N, eq1_q0_from_temperature, eq2_L0
from src.makkonen_model import eq15_forming_hoarfrost_density
from src.simulation_runner import run_makkonen_timeseries


def main() -> None:
    cable = case_01_cable_params()
    alpha = alpha_star_1_per_N(cable.A_N, cable.B_N_m2, cable.C_N_m)
    q0 = eq1_q0_from_temperature(cable.q0T_N_per_m, cable.beta_1_per_C, -20.0, cable.T0_C)
    _ = eq2_L0(cable.l_m, q0, alpha, 1.0)
    assert eq15_forming_hoarfrost_density(-10.0) > 0

    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2026-01-01 00:00:00", "2026-01-01 00:05:00"]),
            "ta_C": [-20.0, -20.2],
            "T1_C": [-19.0, -19.5],
            "rh_pct": [95.0, 96.0],
            "pa_Pa": [101325.0, 101325.0],
            "v_m_per_s": [1.0, 1.2],
            "n_tenths": [8.0, 8.0],
            "qS_W_per_m2": [0.0, 0.0],
            "current_A": [100.0, 100.0],
            "delta_tau_s": [300.0, 300.0],
            "phi_H_deg": [1.0, 1.0],
            "phi_K1_deg": [1.5, 1.5],
        }
    )
    df_cal = build_calibrated_dataset(df, CalibrationConfig(R_ohm_per_m=cable.R_ohm_per_m))
    df_sim = run_makkonen_timeseries(df_cal, cable, initial_state=case_01_initial_hoarfrost_state())
    assert len(df_sim) == 2
    assert {"H_m", "rho_t_kg_per_m3", "mass_per_m_kg_per_m"}.issubset(df_sim.columns)
    print("smoke_test passed")


if __name__ == "__main__":
    main()

