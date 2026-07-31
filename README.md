# Smart Meter Simulator

Portable lab board that **acts like a Dutch/Belgian DSMR smart meter P1 port**.  
Park it on battery in a building corner, plug in [P1 Ghost](https://github.com/arman087/P1_ghost), and test Ghost Wi‑Fi range without a real meter.

| This board (meter) | P1 Ghost / OSM (reader) |
|--------------------|-------------------------|
| Female RJ12 | Male RJ12 |
| **Supplies** +5 V on pin 1 | Takes +5 V |
| **Senses** Data Request on pin 2 | Drives Request high |
| **Open-collector / opto** Data on pin 5 | Reads Data |

**MCU:** ESP32-C3-MINI-1 (Wi‑Fi on for config / OTA) · **P1 serial:** 115200 8N1 inverted open-drain  
**Telegram store:** microSD · **Build volume:** ~5 boards (JLCPCB)

**Why / how so far:** **[DESIGN_REPORT.md](DESIGN_REPORT.md)**  
**Working KiCad:** `my_design/Slimme_meter_Sim/` (power through **SYS_5V** drawn)

---

## Locked power architecture

Charge, boost, MCU, and P1 on **one main PCB** (plus 1S LiPo — no power daughterboard):

```
USB-C ──► bq25185 ──► VSYS / V+ (≈3.0–4.5 V) ──► TPS61023 ──► SYS_5V (+5 V)
              │                                      │
           LiPo (2-wire)              ┌──────────────┴──────────────┐
                                      ▼                             ▼
                               5→3.3 (≥500 mA)              TPS2662 foldback
                                      ▼                             ▼
                                  VCC_3V3                        P1_5V → RJ12 pin1
                                  ESP32 / SD
```

| Net | What it is | Notes |
|-----|------------|--------|
| `VSYS` / `V+` | bq25185 system rail | **Not 5 V** — ~4.5 V on USB, ~3.0–4.2 V on battery |
| `SYS_5V` | TPS61023 boost out | **Required** — real P1 5 V + headroom for 3.3 V |
| `VCC_3V3` | On-board 5→3.3 | From `SYS_5V`, ≥500 mA (Wi‑Fi) |
| `P1_5V` | TPS2662 out | DSMR foldback ~250 mA |

**Do not** feed RJ12 or a 3.3 V LDO from `V+` alone — Ghost needs ~5 V on battery, and a 3.3 V LDO browns out when the cell is low.

Board USB-C for ESP32 **D+/D−** may be separate from charge USB-C (or carefully shared).

---

## Architecture

```
bq25185 + TPS61023 (on PCB) ──► SYS_5V
                                  ├─► 5→3.3 ──► ESP32-C3 + microSD (± OLED)
                                  └─► TPS2662 ──► P1_5V ──► RJ12 pin1
Board USB-C ── D+/D− ──► ESP32
RJ12 pin2 ── opto ──► Request GPIO
ESP32 TX ── opto / OC ──► RJ12 pin5
```

Full blueprint: **[DESIGN_GUIDE.md](DESIGN_GUIDE.md)** · Parts: **[PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)** · Design: **[my_design/Slimme_meter_Sim/](my_design/Slimme_meter_Sim/)**

---

## Subcircuits

| Folder | Status |
|--------|--------|
| [circuits/01_usb_c_input](circuits/01_usb_c_input) | Board USB-C data → ESP32 |
| [circuits/02_battery_and_power_mux](circuits/02_battery_and_power_mux) | **bq25185 + TPS61023** |
| [circuits/03_5v_to_3v3](circuits/03_5v_to_3v3) | On-board 5→3.3 for MCU |
| [circuits/04_p1_5v_current_limit](circuits/04_p1_5v_current_limit) | TPS2662 foldback P1 +5 V |
| [circuits/05_esp32_c3_mini](circuits/05_esp32_c3_mini) | ESP32-C3-MINI-1 |
| [circuits/06_rj12_connector](circuits/06_rj12_connector) | RJ12 meter jack |
| [circuits/07_data_request_sense](circuits/07_data_request_sense) | Pin 2 → opto → GPIO |
| [circuits/08_open_collector_data](circuits/08_open_collector_data) | TX → opto OC → pin 5 |
| [circuits/09_esd_protection](circuits/09_esd_protection) | USB + RJ12 ESD |
| [circuits/10_ui_led_button](circuits/10_ui_led_button) | LED + button (± OLED) |
| [circuits/11_optional_isolation](circuits/11_optional_isolation) | Optos + optional iso 5 V DC-DC |
| [circuits/12_microsd](circuits/12_microsd) | microSD telegram store |

Suggested KiCad order: **02 → 03 → 04 → 01 → 05 → 12 → 06 → 11/07/08 → 09 → 10**

---

## Spec reminders

- Data Request HIGH ≈ 5 V → send; OSM releases high‑Z to stop  
- Data = open-collector (opto heritage in DSMR)  
- P1 +5 V: ~250 mA continuous, then **foldback** — **TPS2662** ([TI slvaf94](https://www.ti.com/lit/pdf/slvaf94))  
- Keep **TPS61023**; skip LoRa  

## References

- [P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)
- [TI slvaf94 — TPS2662](https://www.ti.com/lit/pdf/slvaf94)
- [TI bq25185](https://www.ti.com/product/BQ25185) · [TI TPS61023](https://www.ti.com/product/TPS61023)
- [arman087/P1_ghost](https://github.com/arman087/P1_ghost)
