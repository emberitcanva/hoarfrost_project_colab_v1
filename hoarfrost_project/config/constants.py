"""Case 01 constants.

Numerical values are taken from ``docs/variables_case_01_registry.md`` and
are meant to be mirrored into ``docs/input_case_01_numeric_registry.md``.
Formula modules should receive these values through dataclasses rather than
importing constants directly.
"""

from __future__ import annotations

from src.common_types import CablePhysicalParams, HoarfrostState


CASE_ID = "case_01"
SPAN_ID = "ВЛ 35 кВ"

# Geometry and mechanical passport data
L_M = 335.0
D_PR_M = 0.0114
F_M2 = 0.00007939
BETA_1_PER_C = 0.0000192
T0_C = 20.0
A_N = 6_880_000.0
B_N_M2 = 2.331
C_N_M = 3.998
Q0T_N_PER_M = 2.7

# Electrical and environmental constants
R_OHM_PER_M = 0.0004218
G_M_PER_S2 = 9.81
SIGMA_W_PER_M2_K4 = 0.00000005670367
CP_J_PER_KG_K = 1000.0
KA_W_PER_M_K = 0.026
LE_J_PER_KG = 2_833_000.0
RHO_C_KG_PER_M3 = 2700.0
C_C_J_PER_KG_K = 920.0

# Initial hoarfrost state
H_T0_M = 0.0
RHO_T_T0_KG_PER_M3 = 0.0
PREV_DELTA_T_C_K = 0.0

# Confirmed numerical/architecture decisions
RESET_IF_TA_ABOVE_ZERO = True
RESET_IF_T1_ABOVE_ZERO = True
FORCED_A_WINDWARD = 0.032
FORCED_A_LEEWARD = 0.007
DEFAULT_PRESSURE_PA = 101325.0
CURRENT_MATCH_TOLERANCE_S = 325


def alpha_star_1_per_N(A_N: float = A_N, B_N_m2: float = B_N_M2, C_N_m: float = C_N_M) -> float:
    """Confirmed alpha* formula: alpha* = 1 / (A - C^2 / B)."""
    return 1.0 / (A_N - (C_N_m ** 2) / B_N_m2)


def case_01_cable_params() -> CablePhysicalParams:
    """Return case_01 cable and material parameters."""
    return CablePhysicalParams(
        l_m=L_M,
        d_pr_m=D_PR_M,
        F_m2=F_M2,
        beta_1_per_C=BETA_1_PER_C,
        T0_C=T0_C,
        A_N=A_N,
        B_N_m2=B_N_M2,
        C_N_m=C_N_M,
        q0T_N_per_m=Q0T_N_PER_M,
        R_ohm_per_m=R_OHM_PER_M,
        g_m_per_s2=G_M_PER_S2,
        sigma_W_per_m2_K4=SIGMA_W_PER_M2_K4,
        cp_J_per_kg_K=CP_J_PER_KG_K,
        ka_W_per_m_K=KA_W_PER_M_K,
        Le_J_per_kg=LE_J_PER_KG,
        rho_c_kg_per_m3=RHO_C_KG_PER_M3,
        c_c_J_per_kg_K=C_C_J_PER_KG_K,
    )


def case_01_initial_hoarfrost_state() -> HoarfrostState:
    """Return confirmed initial state for case_01."""
    return HoarfrostState(
        H_m=H_T0_M,
        rho_t_kg_per_m3=RHO_T_T0_KG_PER_M3,
        mass_per_m_kg_per_m=0.0,
        prev_delta_T_c_K=PREV_DELTA_T_C_K,
    )

