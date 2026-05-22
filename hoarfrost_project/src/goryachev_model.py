"""Goryachev mechanical model, formulas (1)-(12).

Only formulas from ``docs/goryachev_formulas_corrected.md`` are implemented.
User decisions dated 2026-05-23 are applied:

* external angle API is in degrees;
* internal angle calculations are in radians;
* formula (2) uses only the plus branch;
* formulas (8)-(11) remain NotImplementedError stubs;
* formula (12) uses 9.81 instead of the registry's 9.84 by explicit decision.
"""

from __future__ import annotations

import math


EPS = 1e-12


def degrees_to_radians(angle_deg: float) -> float:
    return math.radians(float(angle_deg))


def radians_to_degrees(angle_rad: float) -> float:
    return math.degrees(float(angle_rad))


def helper_u_from_phi_H(phi_H_deg: float) -> float:
    """u = ln(tg(pi/4 + phi_H/2))."""
    phi_H_rad = degrees_to_radians(phi_H_deg)
    tan_value = math.tan(math.pi / 4.0 + phi_H_rad / 2.0)
    if tan_value <= 0.0:
        raise ValueError(f"helper_u_from_phi_H: tan argument result must be > 0, got {tan_value}")
    return math.log(tan_value)


def alpha_star_1_per_N(A_N: float, B_N_m2: float, C_N_m: float) -> float:
    """Confirmed formula: alpha* = 1 / (A - C^2 / B)."""
    denominator = A_N - (C_N_m ** 2) / B_N_m2
    if abs(denominator) < EPS:
        raise ValueError("alpha_star_1_per_N: denominator A - C^2/B is too close to zero")
    return 1.0 / denominator


def eq1_q0_from_temperature(q0T_N_per_m: float, beta_1_per_C: float, T1_C: float, T0_C: float) -> float:
    """q0 = q0T / (1 + beta * (T1 - T0))."""
    denominator = 1.0 + beta_1_per_C * (T1_C - T0_C)
    if abs(denominator) < EPS:
        raise ValueError("eq1_q0_from_temperature: denominator is too close to zero")
    return q0T_N_per_m / denominator


def eq2_L0(l_m: float, q0_N_per_m: float, alpha_star: float, phi_H_deg: float) -> float:
    """L0 = (-u + sqrt(2 * alpha* * l * q0 * sh(u) + u^2)) / (alpha* * q0)."""
    u = helper_u_from_phi_H(phi_H_deg)
    radicand = 2.0 * alpha_star * l_m * q0_N_per_m * math.sinh(u) + u ** 2
    if radicand < 0.0:
        raise ValueError(f"eq2_L0: negative radicand {radicand}")
    denominator = alpha_star * q0_N_per_m
    if abs(denominator) < EPS:
        raise ValueError("eq2_L0: denominator alpha* * q0 is too close to zero")
    return (-u + math.sqrt(radicand)) / denominator


def eq3_L0T(L0_m: float, beta_1_per_C: float, T1_C: float, T0_C: float) -> float:
    """L0T = L0 / (1 + beta * (T1 - T0))."""
    denominator = 1.0 + beta_1_per_C * (T1_C - T0_C)
    if abs(denominator) < EPS:
        raise ValueError("eq3_L0T: denominator is too close to zero")
    return L0_m / denominator


def eq4_phi_K0(
    phi_K1_deg: float,
    phi_H_deg: float,
    alpha_star: float,
    q0T_N_per_m: float,
    L0T_m: float,
    l_m: float,
    C_N_m: float,
    B_N_m2: float,
) -> float:
    """Formula (4), returning phi_K0 in degrees.

    The algebraic angular correction is treated in radians internally.
    """
    u = helper_u_from_phi_H(phi_H_deg)
    sh_u = math.sinh(u)
    ch_u = math.cosh(u)
    if abs(sh_u) < EPS:
        raise ValueError("eq4_phi_K0: sinh(u) is too close to zero")
    inner = alpha_star * q0T_N_per_m * L0T_m / (2.0 * sh_u)
    delta_phi_rad = inner * (l_m + L0T_m * (ch_u - inner)) * (C_N_m / (2.0 * B_N_m2))
    phi_K0_rad = degrees_to_radians(phi_K1_deg) - delta_phi_rad
    return radians_to_degrees(phi_K0_rad)


def eq5_L0g(L0T_m: float, beta_1_per_C: float, T1_C: float, T0_C: float) -> float:
    """L0g = L0T * (1 + beta * (T1 - T0))."""
    return L0T_m * (1.0 + beta_1_per_C * (T1_C - T0_C))


def eq6_tension(
    l_m: float,
    L0g_m: float,
    phi_H_deg: float,
    phi_K1_deg: float,
    phi_K0_deg: float,
    B_N_m2: float,
    C_N_m: float,
    alpha_star: float,
) -> float:
    """Formula (6): F tension."""
    u = helper_u_from_phi_H(phi_H_deg)
    ch_u = math.cosh(u)
    phi_K1_rad = degrees_to_radians(phi_K1_deg)
    phi_K0_rad = degrees_to_radians(phi_K0_deg)
    delta_phi_rad = phi_K1_rad - phi_K0_rad
    base = l_m + L0g_m * ch_u
    radicand = base ** 2 - 8.0 * L0g_m * delta_phi_rad * B_N_m2 / C_N_m
    if radicand < 0.0:
        raise ValueError(f"eq6_tension: negative radicand {radicand}")
    denominator = 2.0 * alpha_star * L0g_m
    if abs(denominator) < EPS:
        raise ValueError("eq6_tension: denominator is too close to zero")
    return (base - math.sqrt(radicand)) / denominator * ch_u


def eq7_sag(phi_H_deg: float, L0_m: float, alpha_star: float, q0_N_per_m: float) -> float:
    """f = ((ch(u) - 1) * L0) / (2 * sh(u)) + alpha* * q0 * L0^2 / 8."""
    u = helper_u_from_phi_H(phi_H_deg)
    sh_u = math.sinh(u)
    if abs(sh_u) < EPS:
        raise ValueError("eq7_sag: sinh(u) is too close to zero")
    return ((math.cosh(u) - 1.0) * L0_m) / (2.0 * sh_u) + alpha_star * q0_N_per_m * L0_m ** 2 / 8.0


def eq8_sensitivity_phi_K(*args, **kwargs) -> float:
    raise NotImplementedError("REQUIRES_USER_DECISION: formula (8) sensitivity is not implemented.")


def eq9_sensitivity_phi_H(*args, **kwargs) -> float:
    raise NotImplementedError("REQUIRES_USER_DECISION: formula (9) sensitivity is not implemented.")


def eq10_sensitivity_T(*args, **kwargs) -> float:
    raise NotImplementedError("REQUIRES_USER_DECISION: formula (10) sensitivity is not implemented.")


def eq11_total_error(*args, **kwargs) -> float:
    raise NotImplementedError("REQUIRES_USER_DECISION: formula (11) requires formulas (8)-(10).")


def eq12_ice_wall_thickness(d_pr_m: float, Fg_N: float, q0g_kg_per_m3: float, L0g_m: float) -> float:
    """c = (-d_pr + sqrt(d_pr^2 + 4 * Fg / (q0g * 9.81 * pi * L0g))) / 2."""
    if q0g_kg_per_m3 <= 0.0:
        raise ValueError("eq12_ice_wall_thickness: q0g must be > 0")
    if L0g_m <= 0.0:
        raise ValueError("eq12_ice_wall_thickness: L0g must be > 0")
    radicand = d_pr_m ** 2 + 4.0 * Fg_N / (q0g_kg_per_m3 * 9.81 * math.pi * L0g_m)
    if radicand < 0.0:
        raise ValueError(f"eq12_ice_wall_thickness: negative radicand {radicand}")
    return (-d_pr_m + math.sqrt(radicand)) / 2.0

