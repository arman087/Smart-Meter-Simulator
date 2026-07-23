# Smart Meter Simulator

Lab board that **acts like a Dutch/Belgian DSMR smart meter P1 port**.  
Use it to develop readers such as [P1 Ghost](https://github.com/arman087/P1_ghost) without a real meter.

| This board (meter) | P1 Ghost / OSM (reader) |
|--------------------|-------------------------|
| Female RJ12 | Male RJ12 |
| **Supplies** +5 V on pin 1 | Takes +5 V |
| **Senses** Data Request on pin 2 | Drives Request high |
| **Open-collector** Data on pin 5 | Reads Data |

**MCU:** ESP32-C3-MINI-1 (Wi‑Fi) · **Serial:** 115200 8N1, inverted open-drain · **P1 power:** ~250 mA @ 5 V (DSMR)

This is a **one-off / low-volume lab tool**. Prefer ready modules and nice ICs over cheapest discrete BOM.

---

## Architecture

```
USB-C ──► battery / power path ──► SYS_5V ──► P1 current limit ──► RJ12 pin1 (+5V)
                │                      │
             LiPo                   3.3 V ──► ESP32-C3-MINI-1
                                              │         │
                                    Request sense    OC Data driver
                                         ▲                │
                                    RJ12 pin2         RJ12 pin5
```

Full blueprint (day plan, pin map, checklist): **[DESIGN_GUIDE.md](DESIGN_GUIDE.md)**

---

## Subcircuits (start here)

Each folder has a `NOTES.txt`: what it does, parts to buy, and human / KiCad references.

| Folder | Block |
|--------|--------|
| [circuits/01_usb_c_input](circuits/01_usb_c_input) | USB-C power + data to ESP32 |
| [circuits/02_battery_and_power_mux](circuits/02_battery_and_power_mux) | Charge + USB/battery load share → 5 V |
| [circuits/03_regulator_3v3](circuits/03_regulator_3v3) | SYS_5V → 3.3 V for MCU |
| [circuits/04_p1_5v_current_limit](circuits/04_p1_5v_current_limit) | Meter-side +5 V out (~250–500 mA limited) |
| [circuits/05_esp32_c3_mini](circuits/05_esp32_c3_mini) | ESP32-C3-MINI-1, USB, reset, RF keep-out |
| [circuits/06_rj12_connector](circuits/06_rj12_connector) | RJ12 6P6C pinout (meter female) |
| [circuits/07_data_request_sense](circuits/07_data_request_sense) | Pin 2 → MCU “start sending” |
| [circuits/08_open_collector_data](circuits/08_open_collector_data) | MCU TX → pin 5 open-collector |
| [circuits/09_esd_protection](circuits/09_esd_protection) | USB + RJ12 ESD |
| [circuits/10_ui_led_button](circuits/10_ui_led_button) | Status LED + user button |
| [circuits/11_optional_isolation](circuits/11_optional_isolation) | Optos (optional realism) |

Suggested order: **01 → 05 → 03 → 06 → 08 → 07 → 04 → 09 → 10**, then **02** if you want portable battery.

---

## Spec reminders (easy to get wrong)

- P1 continuous current is **250 mA**, not 1.25 A ([DSMR P1 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)).
- Data Request **HIGH ≈ 5 V** means “send”; OSM must release to high‑Z to stop (not drive hard to GND).
- Data is **open-collector / open-drain** and logically inverted vs normal UART.

---

## References

- Official electrical rules: [P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)
- Meter-side MOSFET example: [SanderBorra/DSMRSim](https://github.com/SanderBorra/DSMRSim)
- Protocol / pin notes: [lvzon/dsmr-p1-parser](https://github.com/lvzon/dsmr-p1-parser)
- Reader side (mirror of this board): [arman087/P1_ghost](https://github.com/arman087/P1_ghost)
