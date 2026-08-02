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

**Why / how:** **[DESIGN_REPORT.md](DESIGN_REPORT.md)** · **KiCad:** `my_design/Slimme_meter_Sim/`

---

## Progress (schematic — Aug 2026)

| Block | Status |
|-------|--------|
| USB-C → bq25185 → TPS61023 → **SYS_5V** | Drawn (`SCH_1_USB_5volt_sch`) |
| **TPS26625** eFuse → `P1_5V`, caps, green power LED, test points, RJ12 placed | Drawn (sheet 2 / power) |
| **SY8088** buck → **VCC_3V3** | Drawn |
| **ESP32-C3-MINI-1** on 3V3; EN RC; GPIO2/8 pull-ups; USB D−/D+ = GPIO18/19 | Drawn |
| RGB status **LED5050** (WS-class) on GPIO10 via 300 Ω; VDD from SYS_5V via Schottky (~4.5 V) + 100 nF | Drawn |
| PCB placement started (not routed yet) | In progress |
| Request opto (pin 2) + Data OC opto (pin 5) | **Next** |
| microSD, ESD polish, optional button | Later |

Sheets: `SCH_1_USB_5volt_sch.kicad_sch` · `SCH_2_power_supplies.kicad_sch`

---

## Locked power architecture

```
USB-C ──► bq25185 ──► VSYS / V+ (≈3.0–4.5 V) ──► TPS61023 ──► SYS_5V (+5 V)
              │                                      │
           LiPo (2-wire)              ┌──────────────┴──────────────┐
                                      ▼                             ▼
                               SY8088 → 3.3 V              TPS26625 (hiccup)
                                      ▼                             ▼
                                  VCC_3V3                        P1_5V → RJ12 pin1
                                  ESP32 / SD
```

| Net | What it is |
|-----|------------|
| `VSYS` / `V+` | bq25185 system rail — **not** 5 V |
| `SYS_5V` | TPS61023 boost |
| `VCC_3V3` | SY8088 from `SYS_5V` |
| `P1_5V` | TPS26625 out (~250 mA DSMR-like) |

---

## What’s left: Request + Data optos (important)

**Do not** wire ESP32 UART TX (3.3 V push-pull) straight to RJ12 pin 5.

There are **two domains**:

1. **MCU side = 3.3 V** — ESP32 GPIO / UART only talks to the **LED** of each opto.  
2. **P1 side = 5 V** — RJ12 pins 1/2/5 live here (`P1_5V`, Request, Data). Opto **transistor** open-collector sits on this side.

### A) Data Request (pin 2 → GPIO) — “Ghost says start sending”

```
RJ12 pin2 (P1_REQ, ~5 V when active)
    │
    R_LED ──►| opto LED |── GND          ← 5 V / P1 side
                   ║
              opto transistor
                   ║
VCC_3V3 ── Rpu ── collector ──► ESP32 GPIO   ← 3.3 V side
                   emitter ── GND
```

- You **never drive** pin 2 from the MCU.  
- Use a **fast** opto (TLP2361 / 6N137 class — not slow PC817).  
- Firmware: GPIO high/low (document polarity) → start/stop telegram TX.

### B) Data out (GPIO TX → pin 5) — open-collector / opto

```
ESP32 TX (3.3 V) ── R_LED ──►| opto LED |── GND     ← 3.3 V side only
                                  ║
                             opto transistor
                                  ║
RJ12 pin5 (P1_DATA) ── collector     (open collector)
                         emitter ── GND
                         optional: 4.7 kΩ to P1_5V for bench without Ghost
```

- **UART pin stays at 3.3 V** — it only lights the opto LED.  
- **Pin 5 is the 5 V / OC world** — transistor pulls Data low; Ghost’s pull-up (or your 4.7 kΩ) makes high.  
- 115200 baud → **fast** opto.  
- Detail notes: `circuits/07_data_request_sense/` · `circuits/08_open_collector_data/`

---

## Subcircuits

| Folder | Status |
|--------|--------|
| [circuits/01_usb_c_input](circuits/01_usb_c_input) | USB data → ESP32 |
| [circuits/02_battery_and_power_mux](circuits/02_battery_and_power_mux) | bq25185 + TPS61023 |
| [circuits/03_5v_to_3v3](circuits/03_5v_to_3v3) | **SY8088** → 3.3 V |
| [circuits/04_p1_5v_current_limit](circuits/04_p1_5v_current_limit) | **TPS26625** + RILIM calc |
| [circuits/05_esp32_c3_mini](circuits/05_esp32_c3_mini) | ESP32-C3-MINI-1 |
| [circuits/06_rj12_connector](circuits/06_rj12_connector) | RJ12 meter jack |
| [circuits/07_data_request_sense](circuits/07_data_request_sense) | Pin 2 → opto → GPIO **← do next** |
| [circuits/08_open_collector_data](circuits/08_open_collector_data) | TX → opto OC → pin 5 **← do next** |
| [circuits/09_esd_protection](circuits/09_esd_protection) | USB + RJ12 ESD |
| [circuits/10_ui_led_button](circuits/10_ui_led_button) | RGB + optional button |
| [circuits/11_optional_isolation](circuits/11_optional_isolation) | Optos + optional iso DC-DC |
| [circuits/12_microsd](circuits/12_microsd) | microSD |

## References

- [P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)
- [TI slvaf94 — TPS2662](https://www.ti.com/lit/pdf/slvaf94)
- [TI bq25185](https://www.ti.com/product/BQ25185) · [TI TPS61023](https://www.ti.com/product/TPS61023)
- [arman087/P1_ghost](https://github.com/arman087/P1_ghost)
