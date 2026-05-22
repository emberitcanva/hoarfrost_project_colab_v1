# Input numeric registry: case_01

## Identification

- case_id: case_01
- span_id: ВЛ 35 кВ
- cable_mark: AC-70 / уточнить при необходимости

## Geometry

- l_m: 335
- d_pr_m: 0.0114
- F_m2: 0.00007939

## Mechanical parameters

- beta_1_per_C: 0.0000192
- T0_C: 20
- A_N: 6880000
- B_N_m2: 2.331
- C_N_m: 3.998
- q0T_N_per_m: 2.7

## Goryachev calibration state

- T_cal_C: REQUIRES_DATA_OR_ESTIMATION
- phi_H_cal_deg: REQUIRES_DATA_OR_ESTIMATION
- phi_K1_cal_deg: REQUIRES_DATA_OR_ESTIMATION

## State at time t*

- t_star_iso: REQUIRES_USER_INPUT
- T1_C: from prepared time series
- phi_H_deg: from prepared time series
- phi_K1_deg: from prepared time series

## Makkonen meteorology per step

- ta_C: from prepared time series
- ea_Pa: computed over ice from `ta_C` and `rh_pct`
- pa_Pa: from prepared time series, fallback 101325 Pa allowed
- v_m_per_s: from prepared time series, fallback 0 allowed for missing wind
- n_tenths: from prepared METAR/RP5 cloud mapping
- qS_W_per_m2: from data or pvlib calculation
- QJ_W_per_m: computed as `current_A^2 * R_ohm_per_m`
- delta_tau_s: from prepared time grid
- current_A: from `Sensor-VL-module-3-No0036-wide-ffill.csv`

## Constants and material properties

- R_ohm_per_m: 0.0004218
- g_m_per_s2: 9.81
- sigma_W_per_m2_K4: 0.00000005670367
- cp_J_per_kg_K: 1000
- ka_W_per_m_K: 0.026
- Le_J_per_kg: 2833000
- rho_c_kg_per_m3: 2700
- c_c_J_per_kg_K: 920

## Hoarfrost initial conditions

- H_t0_m: 0
- rho_t_t0_kg_per_m3: 0
- prev_delta_T_c_K: 0

## Confirmed derived quantities

- alpha_star_1_per_N: `1 / (A_N - C_N_m^2 / B_N_m2)`
- D_m: `d_pr_m + 2 * H_m`
- mass_per_m_kg_per_m: `(pi / 4) * (D_m^2 - d_pr_m^2) * rho_t_kg_per_m3`
- q0g_at_t_star_kg_per_m3: `rho_t(t*)`

