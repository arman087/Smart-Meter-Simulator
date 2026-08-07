# Slimme meter Sim — big / hand-build (modular only where needed)

**This folder is the active design path.**  
Do not treat the parent `Smart Meter Simulator/` docs as the source of truth for this board.

## Build philosophy

| On main PCB (hand solder / oven) | Modular (headers / kit) |
|----------------------------------|-------------------------|
| LiPo charger IC + passives | **USB-C data** breakout → ESP32 |
| 5 V boost IC + inductor | **microSD** breakout → SPI |
| 5 V → 3.3 V (large package, e.g. SOT-223) | **ESP32** DevKit *or* C3-MINI-1 footprint |
| **TPS2553** P1 current limit | |
| **INA219 / INA226** P1 current sense (I²C) | |
| Optocouplers **6N137 DIP-8** (Request + Data) | |
| RJ12, LED, button, ESD | |

**Not modular:** charger, boost, 3.3 V, eFuse, current sense, optos, RJ12.

## Power flow

```
Charge USB-C (on PCB) ──► charger IC ──► LiPo
                              │
                              └──► 5 V boost ──► SYS_5V
                                      ├─► 3.3 V reg ──► ESP32 DevKit / module
                                      ├─► TPS2553 ──► INA ──► RJ12 pin1 (P1_5V)
                                      └─► opto / UI supplies as needed

Data USB-C module ──► ESP32 (flash / serial)
microSD module     ──► ESP32 SPI
```

## Key part choices (this branch)

| Role | Part | Notes |
|------|------|--------|
| P1 limit | **TPS2553DBVR** | Set ~250–300 mA; constant-current (not DSMR foldback) |
| P1 current monitor | **INA226** or **INA219** | After TPS2553 → RJ12; I²C (GPIO5 OK for SCL/SDA — **not** ADC) |
| 3.3 V | **AMS1117-3.3** SOT-223 (or equal) | From `SYS_5V`; replace tiny SY8089AAC |
| Optos | **6N137** DIP-8 ×2 | Data needs speed @ 115200 |
| Boost | Discrete ~2 A class on PCB | Hot air/oven; avoid cheap MT3608 |
| Charger | Discrete LiPo charger on PCB | Prefer IC with charge terminate + UVLO |

ESP32-C3: analog current is only on **GPIO0–4**. Use GPIO5 for I²C or FAULT, not Hall analog.

## KiCad project

- `Slimme_meter_Sim.kicad_pro` — main project  
- `SCH_1_USB_5volt_sch.kicad_sch` — USB / 5 V related  
- `SCH_2_power_supplies.kicad_sch` — power supplies  

Detail: [ARCHITECTURE.md](ARCHITECTURE.md) · [PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)
