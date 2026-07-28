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
**Telegram store:** microSD (not SDRAM) · **Build volume:** ~5 boards (JLCPCB)

---

## Locked power architecture

```
Adafruit bq25185 + 5V boost (#6106) — integrate on main PCB (preferred)
   USB-C charge + LiPo (2-wire OK; IC has BUVLO)
   5V ──► SYS_5V
            ├─► onboard 5V→3.3V (≈500 mA–1 A) ──► ESP32 / SD / OLED
            └─► TPS2662 foldback ──► [opt. iso DC-DC] ──► RJ12 pin1
```

| Rail | Source | Notes |
|------|--------|--------|
| Charge / LiPo / 5 V | **Adafruit #6106** circuit | Open-source ref in `my_design/libraries/adafruit_bq25185_5v_boost/` |
| `SYS_5V` | Board 5 V boost (~1 A) | Enough for TPS2662 → Ghost |
| `VCC_3V3` | **On-board 5→3.3** | Size for Wi‑Fi + SD + OLED |
| `P1_5V` | **TPS2662** on `SYS_5V` | DSMR foldback ~250 mA |

Board USB-C for ESP32 **D+/D−** may be separate from charge USB-C (or carefully shared).  
Reference libs: **[my_design/](my_design/)** — study there, copy useful parts into your KiCad project.

---

## Architecture

```
Lipo Rider Plus ──5V──► SYS_5V
                          ├─► 5→3.3 ──► ESP32-C3 + microSD (± OLED)
                          └─► TPS2662 ──► P1_5V ──► RJ12 pin1
Board USB-C ── D+/D− ──► ESP32
RJ12 pin2 ── opto ──► Request GPIO
ESP32 TX ── opto / OC ──► RJ12 pin5
```

Full blueprint + day plan: **[DESIGN_GUIDE.md](DESIGN_GUIDE.md)**  
Part picking for KiCad: **[PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)**

---

## Subcircuits

| Folder | Status |
|--------|--------|
| [circuits/01_usb_c_input](circuits/01_usb_c_input) | Board USB-C data → ESP32 |
| [circuits/02_battery_and_power_mux](circuits/02_battery_and_power_mux) | Lipo Rider Plus headers (5V only) |
| [circuits/03_5v_to_3v3](circuits/03_5v_to_3v3) | On-board 5→3.3 for MCU |
| [circuits/04_p1_5v_current_limit](circuits/04_p1_5v_current_limit) | TPS2662 foldback P1 +5 V |
| [circuits/05_esp32_c3_mini](circuits/05_esp32_c3_mini) | ESP32-C3-MINI-1 |
| [circuits/06_rj12_connector](circuits/06_rj12_connector) | RJ12 meter jack |
| [circuits/07_data_request_sense](circuits/07_data_request_sense) | Pin 2 → opto → GPIO |
| [circuits/08_open_collector_data](circuits/08_open_collector_data) | TX → opto OC → pin 5 |
| [circuits/09_esd_protection](circuits/09_esd_protection) | USB + RJ12 ESD |
| [circuits/10_ui_led_button](circuits/10_ui_led_button) | LED + button (± OLED) |
| [circuits/11_optional_isolation](circuits/11_optional_isolation) | Optos + optional iso 5 V DC-DC (**in scope**) |
| [circuits/12_microsd](circuits/12_microsd) | microSD telegram store |

Suggested KiCad order: **02 → 03 → 04 → 01 → 05 → 12 → 06 → 11/07/08 → 09 → 10**

---

## Spec reminders

- Data Request HIGH ≈ 5 V → send; OSM releases high‑Z to stop  
- Data = open-collector (opto heritage in DSMR)  
- P1 +5 V: ~250 mA continuous, then **foldback** — **TPS2662** ([TI slvaf94](https://www.ti.com/lit/pdf/slvaf94))  
- No LoRa on this board  

## References

- [P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)
- [TI slvaf94 — TPS2662](https://www.ti.com/lit/pdf/slvaf94)
- [Seeed Lipo Rider Plus](https://wiki.seeedstudio.com/Lipo-Rider-Plus/)
- [arman087/P1_ghost](https://github.com/arman087/P1_ghost)
