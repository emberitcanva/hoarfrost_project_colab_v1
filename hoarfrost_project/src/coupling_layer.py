"""Coupling layer between Makkonen and Goryachev."""

from __future__ import annotations

from typing import Any

from src.common_types import CablePhysicalParams, GoryachevCalibrationParams, HoarfrostState, MechanicalState
from src.goryachev_model import (
    alpha_star_1_per_N,
    eq1_q0_from_temperature,
    eq2_L0,
    eq3_L0T,
    eq4_phi_K0,
    eq5_L0g,
    eq6_tension,
    eq12_ice_wall_thickness,
)


def hoarfrost_outputs_to_mechanical_inputs(hoarfrost: HoarfrostState) -> dict[str, float]:
    """Confirmed automatic bridge: q0g = rho_t(t*)."""
    return {"q0g_kg_per_m3": hoarfrost.rho_t_kg_per_m3}


def run_goryachev_diagnostic(
    hoarfrost: HoarfrostState,
    cable: CablePhysicalParams,
    calibration: GoryachevCalibrationParams,
    T1_C: float,
    phi_H_deg: float,
    phi_K1_deg: float,
) -> MechanicalState:
    """Run diagnostic Goryachev chain and compare thickness at t*.

    Confirmed coupling decisions:
    * q0g = rho_t(t*);
    * Fg in formula (12) is F from formula (6);
    * q0 is not modified by ice mass;
    * c is diagnostic only.
    """
    q0g = hoarfrost_outputs_to_mechanical_inputs(hoarfrost)["q0g_kg_per_m3"]
    if hoarfrost.H_m <= 0.0 or q0g <= 0.0:
        return MechanicalState(q0g_kg_per_m3=q0g, status="no_ice")
    alpha_star = alpha_star_1_per_N(cable.A_N, cable.B_N_m2, cable.C_N_m)
    q0 = eq1_q0_from_temperature(cable.q0T_N_per_m, cable.beta_1_per_C, T1_C, cable.T0_C)
    L0 = eq2_L0(cable.l_m, q0, alpha_star, calibration.phi_H_cal_deg)
    L0T = eq3_L0T(L0, cable.beta_1_per_C, calibration.T_cal_C, cable.T0_C)
    phi_K0_deg = eq4_phi_K0(
        calibration.phi_K1_cal_deg,
        calibration.phi_H_cal_deg,
        alpha_star,
        cable.q0T_N_per_m,
        L0T,
        cable.l_m,
        cable.C_N_m,
        cable.B_N_m2,
    )
    L0g = eq5_L0g(L0T, cable.beta_1_per_C, T1_C, cable.T0_C)
    F_N = eq6_tension(
        cable.l_m,
        L0g,
        phi_H_deg,
        phi_K1_deg,
        phi_K0_deg,
        cable.B_N_m2,
        cable.C_N_m,
        alpha_star,
    )
    c_m = eq12_ice_wall_thickness(cable.d_pr_m, F_N, q0g, L0g)
    return MechanicalState(
        q0g_kg_per_m3=q0g,
        q0_N_per_m=q0,
        L0_m=L0,
        L0T_m=L0T,
        L0g_m=L0g,
        phi_K0_deg=phi_K0_deg,
        F_N=F_N,
        c_m=c_m,
        status="ok",
        diagnostics={"alpha_star_1_per_N": alpha_star},
    )


def compare_thickness_at_time(H_makkonen_m: float, c_goryachev_m: float) -> dict[str, Any]:
    """Diagnostic comparison of Makkonen H and Goryachev c."""
    signed_diff_m = c_goryachev_m - H_makkonen_m
    rel_signed = signed_diff_m / H_makkonen_m if H_makkonen_m > 0.0 else None
    return {
        "H_makkonen_m": H_makkonen_m,
        "c_goryachev_m": c_goryachev_m,
        "signed_diff_m": signed_diff_m,
        "abs_diff_m": abs(signed_diff_m),
        "rel_diff_signed": rel_signed,
        "rel_diff_abs": abs(rel_signed) if rel_signed is not None else None,
    }

