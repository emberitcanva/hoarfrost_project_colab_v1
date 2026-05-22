"""Makkonen hoarfrost model, formulas (1)-(15).

The formula functions mirror ``docs/makkonen_equations_corrected.md``.
Additional numerical decisions are explicitly recorded in
``docs/requires_user_decision_table.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Literal

import numpy as np

from src.common_types import CablePhysicalParams, HoarfrostState, MeteoInput


SectionName = Literal["windward", "leeward", "upper", "lower"]


@dataclass(frozen=True)
class SectionConfig:
    name: SectionName
    forced_coeff_a: float | None
    use_free_convection: bool
    use_longwave: bool
    use_solar: bool


DEFAULT_SECTIONS: tuple[SectionConfig, ...] = (
    SectionConfig("windward", forced_coeff_a=0.032, use_free_convection=False, use_longwave=False, use_solar=False),
    SectionConfig("leeward", forced_coeff_a=0.007, use_free_convection=False, use_longwave=False, use_solar=False),
    SectionConfig("upper", forced_coeff_a=None, use_free_convection=True, use_longwave=True, use_solar=True),
    SectionConfig("lower", forced_coeff_a=None, use_free_convection=True, use_longwave=False, use_solar=False),
)


NU_TABLE_M2_PER_S = {
    -30.0: 1.08e-5,
    -20.0: 1.16e-5,
    -10.0: 1.24e-5,
    0.0: 1.33e-5,
    10.0: 1.42e-5,
    20.0: 1.51e-5,
    30.0: 1.60e-5,
}


def nu_air_m2_per_s(ta_C: float) -> float:
    """Confirmed numerical helper: linear interpolation of nu(T)."""
    temps = np.array(sorted(NU_TABLE_M2_PER_S), dtype=float)
    values = np.array([NU_TABLE_M2_PER_S[t] for t in temps], dtype=float)
    return float(np.interp(np.clip(float(ta_C), temps[0], temps[-1]), temps, values))


def C_to_K(t_C: float) -> float:
    return float(t_C) + 273.15


def eq1_deposition_rate(h: float, e_s_Pa: float, e_a_Pa: float, c_p: float, p_a_Pa: float) -> float:
    """I = 0.62 * h * (e_s - e_a) / (c_p * p_a)."""
    if c_p * p_a_Pa == 0.0:
        raise ValueError("eq1_deposition_rate: c_p * p_a must be non-zero")
    return 0.62 * h * (e_s_Pa - e_a_Pa) / (c_p * p_a_Pa)


def eq2_energy_balance_residual(q_e: float, q_s: float, q_i: float, q_c: float, q_eff: float) -> float:
    """Residual form of q_e + q_s + q_i = q_c + q_eff."""
    return q_e + q_s + q_i - q_c - q_eff


def eq3_latent_heat_flux(L_e: float, I: float) -> float:
    """q_e = L_e * I."""
    return L_e * I


def eq4_convective_flux(h: float, T_s: float, T_a: float) -> float:
    """q_c = h * (T_s - T_a)."""
    return h * (T_s - T_a)


def eq5_heat_transfer_coefficient(k_a: float, Nu: float, D: float) -> float:
    """h = k_a * Nu / D."""
    if D == 0.0:
        raise ValueError("eq5_heat_transfer_coefficient: D must be non-zero")
    return k_a * Nu / D


def eq6_nusselt_free(Gr: float) -> float:
    """Nu_v = 0.395 * Gr^0.25."""
    if Gr < 0.0:
        raise ValueError("eq6_nusselt_free: Gr must be non-negative")
    return 0.395 * (Gr ** 0.25)


def eq7_grashof_number(g: float, D: float, T_s_K: float, T_a_K: float, nu: float) -> float:
    """Gr = g * D^3 * |T_s - T_a| / (T_a * nu^2)."""
    denominator = T_a_K * nu ** 2
    if denominator == 0.0:
        raise ValueError("eq7_grashof_number: T_a * nu^2 must be non-zero")
    return g * D ** 3 * abs(T_s_K - T_a_K) / denominator


def reynolds_number(v_m_per_s: float, D: float, nu: float) -> float:
    """Auxiliary Re = v * D / nu."""
    if nu == 0.0:
        raise ValueError("reynolds_number: nu must be non-zero")
    return v_m_per_s * D / nu


def eq8_nusselt_forced(a: float, Re: float) -> float:
    """Nu_b = a * Re^0.85."""
    if Re < 0.0:
        raise ValueError("eq8_nusselt_forced: Re must be non-negative")
    return a * (Re ** 0.85)


def eq9_longwave_clear_sky(sigma: float, T_s_K: float, T_a_K: float, e_a_Pa: float) -> float:
    """q_eff,0 = sigma * (T_s^4 - T_a^4 * (0.58 + 0.044 * sqrt(e_a)))."""
    if e_a_Pa < 0.0:
        raise ValueError("eq9_longwave_clear_sky: e_a must be non-negative")
    return sigma * (T_s_K ** 4 - (T_a_K ** 4) * (0.58 + 0.044 * math.sqrt(e_a_Pa)))


def eq10_longwave_cloud_correction(q_eff_0: float, n_tenths: float) -> float:
    """q_eff = (1 - 0.08 * n) * q_eff,0."""
    return (1.0 - 0.08 * n_tenths) * q_eff_0


def eq11_internal_heat_flux(Q_J: float, Q_t: float, D: float) -> float:
    """q_i = (Q_J + Q_t) / (pi * D)."""
    if D == 0.0:
        raise ValueError("eq11_internal_heat_flux: D must be non-zero")
    return (Q_J + Q_t) / (math.pi * D)


def eq12_cable_temperature(T_s: float, D: float, q_i: float, k_i: float, d: float) -> float:
    """T_c = T_s + (D * q_i / (2 * k_i)) * ln(D / d)."""
    if k_i == 0.0 or d <= 0.0 or D <= 0.0:
        raise ValueError("eq12_cable_temperature: k_i must be non-zero and D,d must be positive")
    return T_s + (D * q_i / (2.0 * k_i)) * math.log(D / d)


def eq13_ice_conductivity(rho_t: float) -> float:
    """k_i = 0.0242 + 0.0002 * rho_t + 2.54e-6 * rho_t^2."""
    return 0.0242 + 0.0002 * rho_t + 2.54e-6 * rho_t ** 2


def eq14_thermal_inertia_power(d: float, rho_c: float, c_c: float, Delta_T_c: float, Delta_tau: float) -> float:
    """Q_t = (pi * d^2 / 4) * rho_c * c_c * (Delta_T_c / Delta_tau)."""
    if Delta_tau == 0.0:
        raise ValueError("eq14_thermal_inertia_power: Delta_tau must be non-zero")
    return (math.pi * d ** 2 / 4.0) * rho_c * c_c * (Delta_T_c / Delta_tau)


def eq15_forming_hoarfrost_density(t_s_C: float) -> float:
    """rho = 650 * exp(0.227 * t_s)."""
    return 650.0 * math.exp(0.227 * t_s_C)


def saturation_vapor_pressure_ice_Pa(t_C: float) -> float:
    """Confirmed e_s/e_sat over ice formula from decisions log."""
    return 611.2 * math.exp(22.46 * t_C / (272.62 + t_C))


def effective_diameter_m(d_pr_m: float, H_m: float) -> float:
    """Confirmed bridge: D = d + 2H."""
    return d_pr_m + 2.0 * H_m


def mass_per_m_from_cylindrical_shell(d_pr_m: float, H_m: float, rho_t_kg_per_m3: float) -> float:
    """Confirmed mass formula: mass_per_m = (pi/4) * (D^2 - d^2) * rho_t."""
    if H_m <= 0.0 or rho_t_kg_per_m3 <= 0.0:
        return 0.0
    D = effective_diameter_m(d_pr_m, H_m)
    return (math.pi / 4.0) * (D ** 2 - d_pr_m ** 2) * rho_t_kg_per_m3


def update_rho_t_weighted(
    rho_t_prev: float,
    H_prev_m: float,
    rho_new: float,
    delta_H_growth_m: float,
    H_new_m: float,
) -> float:
    """Confirmed weighted rho_t update during growth."""
    if H_new_m <= 0.0:
        return 0.0
    if delta_H_growth_m <= 0.0:
        return max(rho_t_prev, 0.0)
    return (rho_t_prev * H_prev_m + rho_new * delta_H_growth_m) / H_new_m


def _section_nusselt(section: SectionConfig, Re: float, Gr: float) -> tuple[float, float, float]:
    Nu_b = eq8_nusselt_forced(section.forced_coeff_a, Re) if section.forced_coeff_a is not None else 0.0
    Nu_v = eq6_nusselt_free(Gr) if section.use_free_convection else 0.0
    Nu = max(Nu_b, Nu_v)
    return Nu, Nu_b, Nu_v


def _section_residual(
    T_s_C: float,
    section: SectionConfig,
    meteo: MeteoInput,
    cable: CablePhysicalParams,
    D_m: float,
    q_i: float,
) -> dict[str, float]:
    nu = nu_air_m2_per_s(meteo.ta_C)
    T_s_K = C_to_K(T_s_C)
    T_a_K = C_to_K(meteo.ta_C)
    Gr = eq7_grashof_number(cable.g_m_per_s2, D_m, T_s_K, T_a_K, nu)
    Re = reynolds_number(meteo.v_m_per_s, D_m, nu)
    Nu, Nu_b, Nu_v = _section_nusselt(section, Re, Gr)
    h = eq5_heat_transfer_coefficient(cable.ka_W_per_m_K, Nu, D_m)
    e_s = saturation_vapor_pressure_ice_Pa(T_s_C)
    I = eq1_deposition_rate(h, e_s, meteo.ea_Pa, cable.cp_J_per_kg_K, meteo.pa_Pa)
    q_e = eq3_latent_heat_flux(cable.Le_J_per_kg, I)
    q_c = eq4_convective_flux(h, T_s_C, meteo.ta_C)
    q_s = meteo.qS_W_per_m2 if section.use_solar else 0.0
    q_eff_0 = eq9_longwave_clear_sky(cable.sigma_W_per_m2_K4, T_s_K, T_a_K, meteo.ea_Pa) if section.use_longwave else 0.0
    q_eff = eq10_longwave_cloud_correction(q_eff_0, meteo.n_tenths) if section.use_longwave else 0.0
    residual = eq2_energy_balance_residual(q_e, q_s, q_i, q_c, q_eff)
    return {
        "T_s_C": T_s_C,
        "residual": residual,
        "I_kg_per_m2_s": I,
        "h_W_per_m2_K": h,
        "Nu": Nu,
        "Nu_b": Nu_b,
        "Nu_v": Nu_v,
        "Re": Re,
        "Gr": Gr,
        "q_e_W_per_m2": q_e,
        "q_c_W_per_m2": q_c,
        "q_s_W_per_m2": q_s,
        "q_i_W_per_m2": q_i,
        "q_eff_0_W_per_m2": q_eff_0,
        "q_eff_W_per_m2": q_eff,
        "e_s_Pa": e_s,
    }


def solve_section_surface_temperature(
    section: SectionConfig,
    meteo: MeteoInput,
    cable: CablePhysicalParams,
    D_m: float,
    q_i: float,
    max_iter: int = 30,
) -> dict[str, float]:
    """Numerically solve formula (2) residual for one section using bisection/fallback."""
    t_min = min(meteo.T1_C, meteo.ta_C) - 10.0
    t_max = max(meteo.T1_C, meteo.ta_C) + 10.0
    low = _section_residual(t_min, section, meteo, cable, D_m, q_i)
    high = _section_residual(t_max, section, meteo, cable, D_m, q_i)
    r_low = low["residual"]
    r_high = high["residual"]
    if r_low * r_high > 0.0:
        candidates = [
            low,
            high,
            _section_residual(meteo.T1_C, section, meteo, cable, D_m, q_i),
            _section_residual(meteo.ta_C, section, meteo, cable, D_m, q_i),
        ]
        return min(candidates, key=lambda item: abs(item["residual"]))
    left, right = low, high
    mid = low
    for _ in range(max_iter):
        mid_T = 0.5 * (left["T_s_C"] + right["T_s_C"])
        mid = _section_residual(mid_T, section, meteo, cable, D_m, q_i)
        if abs(mid["residual"]) < 1e-6:
            return mid
        if left["residual"] * mid["residual"] > 0.0:
            left = mid
        else:
            right = mid
    return mid


def compute_delta_T_c_for_step(state: HoarfrostState, meteo: MeteoInput) -> float:
    """Use previous cable temperature difference for formula (14)."""
    if state.Tc_prev_C is None:
        return float(meteo.prev_delta_T_c_K)
    if not math.isfinite(state.prev_delta_T_c_K):
        return 0.0
    return float(state.prev_delta_T_c_K)


def update_hoarfrost_state(
    state: HoarfrostState,
    meteo: MeteoInput,
    cable: CablePhysicalParams,
    sections: tuple[SectionConfig, ...] = DEFAULT_SECTIONS,
    reset_if_ta_above_zero: bool = True,
    reset_if_T1_above_zero: bool = True,
) -> dict[str, Any]:
    """Advance hoarfrost state by one step.

    Confirmed reset mechanism: if ``ta_C > 0`` or ``T1_C > 0`` under the
    corresponding flags, reset H, rho_t, and mass to zero.
    """
    if (reset_if_ta_above_zero and meteo.ta_C > 0.0) or (reset_if_T1_above_zero and meteo.T1_C > 0.0):
        new_state = HoarfrostState(
            H_m=0.0,
            rho_t_kg_per_m3=0.0,
            mass_per_m_kg_per_m=0.0,
            prev_delta_T_c_K=0.0,
            Tc_prev_C=None,
            T1_prev_C=meteo.T1_C,
        )
        return {
            "state": new_state,
            "was_reset": True,
            "diagnostics": {
                "reason": "temperature_reset",
                "reset_due_ta": meteo.ta_C > 0.0,
                "reset_due_T1": meteo.T1_C > 0.0,
            },
        }

    delta_T_c_K = compute_delta_T_c_for_step(state, meteo)
    Q_t = eq14_thermal_inertia_power(
        cable.d_pr_m,
        cable.rho_c_kg_per_m3,
        cable.c_c_J_per_kg_K,
        delta_T_c_K,
        meteo.delta_tau_s,
    )
    D_prev_m = effective_diameter_m(cable.d_pr_m, state.H_m)
    q_i = eq11_internal_heat_flux(meteo.QJ_W_per_m, Q_t, D_prev_m)
    section_results = {
        section.name: solve_section_surface_temperature(section, meteo, cable, D_prev_m, q_i)
        for section in sections
    }
    positive_sections = [name for name, result in section_results.items() if result["I_kg_per_m2_s"] > 0.0]
    icing_active = bool(positive_sections)
    max_I_section = max(positive_sections, key=lambda name: section_results[name]["I_kg_per_m2_s"]) if icing_active else None
    control_section = max_I_section if max_I_section is not None else max(section_results, key=lambda name: section_results[name]["I_kg_per_m2_s"])

    rho_new = 0.0
    delta_H_growth_sum = 0.0
    if max_I_section is not None:
        T_s_for_density_C = section_results[max_I_section]["T_s_C"]
        if T_s_for_density_C <= 0.0:
            rho_new = eq15_forming_hoarfrost_density(T_s_for_density_C)
            for name in positive_sections:
                I_sec = section_results[name]["I_kg_per_m2_s"]
                if section_results[name]["T_s_C"] <= 0.0:
                    delta_H_growth_sum += I_sec * meteo.delta_tau_s / rho_new

    delta_H_growth_m = delta_H_growth_sum / float(len(sections))
    delta_H_sublimation_sum = 0.0
    if state.H_m > 0.0 and state.rho_t_kg_per_m3 > 0.0:
        for result in section_results.values():
            I_sec = result["I_kg_per_m2_s"]
            if I_sec < 0.0:
                delta_H_sublimation_sum += (-I_sec) * meteo.delta_tau_s / state.rho_t_kg_per_m3
    delta_H_sublimation_m = delta_H_sublimation_sum / float(len(sections))
    H_new_m = max(0.0, state.H_m + delta_H_growth_m - delta_H_sublimation_m)
    rho_t_new = update_rho_t_weighted(
        state.rho_t_kg_per_m3,
        state.H_m,
        rho_new,
        delta_H_growth_m,
        H_new_m,
    )
    mass_new = mass_per_m_from_cylindrical_shell(cable.d_pr_m, H_new_m, rho_t_new)

    D_new_m = effective_diameter_m(cable.d_pr_m, H_new_m)
    k_i = eq13_ice_conductivity(rho_t_new)
    control = section_results[control_section]
    q_i_new = eq11_internal_heat_flux(meteo.QJ_W_per_m, Q_t, D_new_m)
    Tc_C = eq12_cable_temperature(control["T_s_C"], D_new_m, q_i_new, k_i, cable.d_pr_m)
    prev_delta_T_c_new = 0.0 if state.Tc_prev_C is None else state.Tc_prev_C - Tc_C
    new_state = HoarfrostState(
        H_m=H_new_m,
        rho_t_kg_per_m3=rho_t_new,
        mass_per_m_kg_per_m=mass_new,
        prev_delta_T_c_K=prev_delta_T_c_new,
        Tc_prev_C=Tc_C,
        T1_prev_C=meteo.T1_C,
    )
    return {
        "state": new_state,
        "was_reset": False,
        "diagnostics": {
            "reason": "ok",
            "D_prev_m": D_prev_m,
            "D_new_m": D_new_m,
            "Q_t_W_per_m": Q_t,
            "q_i_W_per_m2": q_i,
            "q_i_new_W_per_m2": q_i_new,
            "k_i_W_per_m_K": k_i,
            "Tc_C": Tc_C,
            "delta_T_c_K_used": delta_T_c_K,
            "prev_delta_T_c_new_K": prev_delta_T_c_new,
            "icing_active": icing_active,
            "max_I_section": max_I_section,
            "control_section": control_section,
            "rho_new_kg_per_m3": rho_new,
            "delta_H_growth_m": delta_H_growth_m,
            "delta_H_sublimation_m": delta_H_sublimation_m,
            "delta_H_m": delta_H_growth_m - delta_H_sublimation_m,
            "section_results": section_results,
        },
    }

