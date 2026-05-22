"""Shared dataclasses for Makkonen, Goryachev, coupling, and simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MeteoInput:
    """One time-step of meteorological and thermal inputs.

    External field names follow the project variable registry conventions.
    """

    ta_C: float
    T1_C: float
    ea_Pa: float
    pa_Pa: float
    v_m_per_s: float
    n_tenths: float
    qS_W_per_m2: float
    QJ_W_per_m: float
    delta_tau_s: float
    prev_delta_T_c_K: float = 0.0


@dataclass
class CablePhysicalParams:
    """Cable, material, and environmental constants for one span/case."""

    l_m: float
    d_pr_m: float
    F_m2: float
    beta_1_per_C: float
    T0_C: float
    A_N: float
    B_N_m2: float
    C_N_m: float
    q0T_N_per_m: float
    R_ohm_per_m: float
    g_m_per_s2: float
    sigma_W_per_m2_K4: float
    cp_J_per_kg_K: float
    ka_W_per_m_K: float
    Le_J_per_kg: float
    rho_c_kg_per_m3: float
    c_c_J_per_kg_K: float


@dataclass
class GoryachevCalibrationParams:
    """Calibration/reference state for the Goryachev mechanical model."""

    T_cal_C: float
    phi_H_cal_deg: float
    phi_K1_cal_deg: float


@dataclass
class SensorSnapshot:
    """Sensor variables used by the pipeline at one timestamp."""

    timestamp: Any
    T1_C: float
    phi_H_deg: float
    phi_K1_deg: float
    current_A: float | None = None


@dataclass
class HoarfrostState:
    """Dynamic hoarfrost state carried from step to step."""

    H_m: float = 0.0
    rho_t_kg_per_m3: float = 0.0
    mass_per_m_kg_per_m: float = 0.0
    prev_delta_T_c_K: float = 0.0
    Tc_prev_C: float | None = None
    T1_prev_C: float | None = None


@dataclass
class MechanicalState:
    """Mechanical diagnostic outputs from Goryachev."""

    q0g_kg_per_m3: float | None = None
    q0_N_per_m: float | None = None
    L0_m: float | None = None
    L0T_m: float | None = None
    L0g_m: float | None = None
    phi_K0_deg: float | None = None
    F_N: float | None = None
    c_m: float | None = None
    status: str = "not_run"
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass
class CoupledState:
    """Combined state after one coupled simulation step."""

    hoarfrost: HoarfrostState
    mechanical: MechanicalState | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

