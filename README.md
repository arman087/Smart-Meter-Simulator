# Smart Meter Simulator

Lab board that **acts like a Dutch/Belgian DSMR smart meter P1 port**.  
Use it to develop readers such as [P1 Ghost](https://github.com/arman087/P1_ghost) without a real meter.

| This board (meter) | P1 Ghost / OSM (reader) |
|--------------------|-------------------------|
| Female RJ12 | Male RJ12 |
| **Supplies** +5 V on pin 1 | Takes +5 V |
| **Senses** Data Request on pin 2 | Drives Request high |
| **Open-collector** Data on pin 5 | Reads Data |

**MCU:** ESP32-C3-MINI-1 · **P1 serial:** 115200 8N1 inverted open-drain · **P1 power:** ~250 mA @ 5 V

---

## Power (buy this — do not design)

**[Seeed Lipo Rider Plus](https://wiki.seeedstudio.com/Lipo-Rider-Plus/)** daughterboard:

| Port | Use |
|------|-----|
| USB-C | Charge LiPo only (no D+/D− to ESP32) |
| Header **5V** | `SYS_5V` → P1 current limit → RJ12 pin 1 |
| Header **3V3** | ESP32 `VCC_3V3` |
| JST LiPo | 1S battery for corner / portable testing |
| USB-A | Unused |

Board USB-C (circuit 01) still carries **D+/D−** for flashing the ESP32.

Mechanical footprint + mounting holes:  
**[mechanicals/lipo_rider_plus/](mechanicals/lipo_rider_plus/)** (`Seeed_Lipo_Rider_Plus.kicad_mod`)

---

## Architecture

```
LiPo + Lipo Rider Plus ──► 5V ──► P1 current limit ──► RJ12 pin1
         │                  └──► 3.3V ──► ESP32-C3-MINI-1
         │                                      │         │
    USB-C charge                         Request sense   OC Data
         (power only)                           ▲            │
                                           RJ12 pin2    RJ12 pin5

Board USB-C ── D+/D− ──► ESP32 (flash / serial)   ← separate from Lipo Rider
```

Full blueprint: **[DESIGN_GUIDE.md](DESIGN_GUIDE.md)**

---

## Subcircuits

| Folder | Block |
|--------|--------|
| [circuits/01_usb_c_input](circuits/01_usb_c_input) | Board USB-C **data** to ESP32 (+ ESD) |
| [circuits/02_battery_and_power_mux](circuits/02_battery_and_power_mux) | **Lipo Rider Plus** (5V + 3.3V + charge) |
| [circuits/03_regulator_3v3](circuits/03_regulator_3v3) | Skip if using Lipo Rider 3V3 pin |
| [circuits/04_p1_5v_current_limit](circuits/04_p1_5v_current_limit) | Limit P1 +5V (~250 mA) |
| [circuits/05_esp32_c3_mini](circuits/05_esp32_c3_mini) | ESP32-C3-MINI-1 |
| [circuits/06_rj12_connector](circuits/06_rj12_connector) | RJ12 meter jack |
| [circuits/07_data_request_sense](circuits/07_data_request_sense) | Pin 2 → GPIO |
| [circuits/08_open_collector_data](circuits/08_open_collector_data) | TX → pin 5 OC |
| [circuits/09_esd_protection](circuits/09_esd_protection) | USB + RJ12 ESD |
| [circuits/10_ui_led_button](circuits/10_ui_led_button) | LED + button |
| [circuits/11_optional_isolation](circuits/11_optional_isolation) | Optional |

Suggested order: **02 (mount Lipo Rider) → 01 → 05 → 06 → 08 → 07 → 04 → 09 → 10**

---

## Spec reminders

- P1 continuous current **250 mA** ([DSMR P1 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf))
- Data Request HIGH ≈ 5 V → send; OSM releases to high‑Z to stop
- Data = open-collector, inverted UART

## References

- [P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)
- [SanderBorra/DSMRSim](https://github.com/SanderBorra/DSMRSim)
- [lvzon/dsmr-p1-parser](https://github.com/lvzon/dsmr-p1-parser)
- [arman087/P1_ghost](https://github.com/arman087/P1_ghost)
- [Seeed Lipo Rider Plus](https://wiki.seeedstudio.com/Lipo-Rider-Plus/)
