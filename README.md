# Smart Meter Simulator

Lab board that **acts like a Dutch/Belgian DSMR smart meter P1 port**.  
Use it to develop readers such as [P1 Ghost](https://github.com/arman087/P1_ghost) without a real meter.

| This board (meter) | P1 Ghost / OSM (reader) |
|--------------------|-------------------------|
| Female RJ12 | Male RJ12 |
| **Supplies** +5 V on pin 1 | Takes +5 V |
| **Senses** Data Request on pin 2 | Drives Request high |
| **Open-collector** Data on pin 5 | Reads Data |

**MCU:** ESP32-C3-MINI-1 · **P1 serial:** 115200 8N1 inverted open-drain

---

## Power

**[Seeed Lipo Rider Plus](https://wiki.seeedstudio.com/Lipo-Rider-Plus/)** — MCU-oriented charger/booster, used as a **daughterboard / sidecar** (buy module; footprint you can draw yourself).

| Port | Use |
|------|-----|
| USB-C | Charge LiPo |
| JST | 1S LiPo battery |
| **5V** | → RJ12 pin 1 (`SYS_5V`) |
| **3V3** | → ESP32 `VCC_3V3` |
| GND | Common |
| USB-A | Unused |

USB unplugged + battery → still **5 V and 3.3 V**.  
Board USB-C (circuit 01) = ESP32 **D+/D−** flash only (not the charger).

Reference photos / Eagle (optional): [mechanicals/lipo_rider_plus/](mechanicals/lipo_rider_plus/)

---

## Architecture

```
Lipo Rider Plus (daughterboard)
   USB-C charge + LiPo
   5V  ──────────────────────────► RJ12 pin1
   3V3 ──► ESP32-C3-MINI-1
              │              │
       Request sense      OC Data TX
              ▲              │
         RJ12 pin2      RJ12 pin5

Board USB-C ── D+/D− ──► ESP32 (flash / serial)
```

No P1 current-limit IC. No separate on-board 3.3 V regulator (use Lipo Rider 3V3).

Full blueprint: **[DESIGN_GUIDE.md](DESIGN_GUIDE.md)**

---

## Subcircuits

| Folder | Status |
|--------|--------|
| [circuits/01_usb_c_input](circuits/01_usb_c_input) | Board USB-C data → ESP32 |
| [circuits/02_battery_and_power_mux](circuits/02_battery_and_power_mux) | **Lipo Rider Plus** daughterboard |
| [circuits/04_p1_5v_current_limit](circuits/04_p1_5v_current_limit) | **Dropped** |
| [circuits/05_esp32_c3_mini](circuits/05_esp32_c3_mini) | ESP32-C3-MINI-1 |
| [circuits/06_rj12_connector](circuits/06_rj12_connector) | RJ12 meter jack |
| [circuits/07_data_request_sense](circuits/07_data_request_sense) | Pin 2 → GPIO |
| [circuits/08_open_collector_data](circuits/08_open_collector_data) | TX → pin 5 OC |
| [circuits/09_esd_protection](circuits/09_esd_protection) | USB + RJ12 ESD |
| [circuits/10_ui_led_button](circuits/10_ui_led_button) | LED + button |
| [circuits/11_optional_isolation](circuits/11_optional_isolation) | Optional |

Suggested order: **02 → 01 → 05 → 06 → 08 → 07 → 09 → 10**

---

## Spec reminders

- Data Request HIGH ≈ 5 V → send; OSM releases high‑Z to stop  
- Data = open-collector, inverted UART  
- P1 continuous ~250 mA on real meters; this lab board does not limit in hardware  

## References

- [P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)
- [SanderBorra/DSMRSim](https://github.com/SanderBorra/DSMRSim)
- [Seeed Lipo Rider Plus](https://wiki.seeedstudio.com/Lipo-Rider-Plus/)
- [arman087/P1_ghost](https://github.com/arman087/P1_ghost)
