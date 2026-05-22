# Hoarfrost Project: Makkonen + Goryachev

Рабочий Python-проект для Colab/Jupyter, собранный из реестров формул и решений пользователя.

## Структура

```text
hoarfrost_project/
  config/
    constants.py
  src/
    common_types.py
    calibration.py
    makkonen_model.py
    goryachev_model.py
    coupling_layer.py
    simulation_runner.py
    validation_checks.py
  docs/
    *.md
  tests/
```

## Основные правила реализации

- Формулы Макконена реализованы как `eq1`–`eq15` в `src/makkonen_model.py`.
- Формулы Горячева реализованы как `eq1`–`eq12` в `src/goryachev_model.py`.
- Формулы Горячева (8)–(11) оставлены как `NotImplementedError`.
- Coupling использует подтверждённый мост `q0g = rho_t(t*)`.
- Диагностическая толщина `c` по Горячеву считается только в заданный `t*`.
- Все численные константы `case_01` вынесены в `config/constants.py`.

## Минимальный запуск в Colab/Jupyter

```python
import sys
sys.path.append("/content/hoarfrost_project")

from config.constants import case_01_cable_params, case_01_initial_hoarfrost_state
from src.calibration import CalibrationConfig, build_calibrated_dataset
from src.common_types import GoryachevCalibrationParams
from src.simulation_runner import run_full_pipeline

cable = case_01_cable_params()
initial_state = case_01_initial_hoarfrost_state()

config = CalibrationConfig(R_ohm_per_m=cable.R_ohm_per_m)
df_cal = build_calibrated_dataset(df_prepared, config)

calibration = GoryachevCalibrationParams(
    T_cal_C=...,          # estimated or user-specified
    phi_H_cal_deg=...,    # estimated or user-specified
    phi_K1_cal_deg=...,   # estimated or user-specified
)

result = run_full_pipeline(
    df_calibrated=df_cal,
    cable=cable,
    calibration=calibration,
    t_star="YYYY-MM-DD HH:MM:SS",
    initial_state=initial_state,
)

df_sim = result["simulation"]
diagnostic = result["goryachev_diagnostic"]
```

## Required input columns for `build_calibrated_dataset`

```text
timestamp
ta_C
T1_C
rh_pct
pa_Pa
v_m_per_s
n_tenths
qS_W_per_m2
current_A
delta_tau_s
phi_H_deg
phi_K1_deg
```

## Notes

This project is intentionally ML-ready: simulation outputs keep intermediate
fields and section diagnostics so parameter-identification workflows can be
added later without rewriting the physical model modules.

