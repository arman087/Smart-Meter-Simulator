# Next steps (paused Aug 2026)

ESP32-C3 design path is largely locked in docs + KiCad. Come back here when continuing.

---

## Do first (stay on ESP32)

1. Finish PCB routing / DRC in `my_design/Slimme_meter_Sim/`.
2. Lock `ESP32_enable` (Request sense) to a specific GPIO in schematic + [FIRMWARE_GUIDE.md](FIRMWARE_GUIDE.md).
3. Order PCB **with stencil** (JLCPCB or similar).
4. Assemble ~1 board:
   - **Hot air + stencil** for the five ICs (bq25185, TPS61023, TPS26625, SY8088, ESP32-C3 module / QFN-class parts + optos as needed).
   - Iron for connectors, RJ12, through-hole / larger parts.
5. Optional DIY ease: upsize passives **0402 → 0603 / 0805 / 1206** before the next fab spin (not required if stencil + paste are good).
6. Bring-up: USB charge → SYS_5V → 3V3 → UART telegrams on Request → Ghost on RJ12 @ ~250 mA P1 limit.
7. Later: microSD telegrams, ESD polish, Wi‑Fi config/OTA.

**Assembly note:** Stencil + paste + hot air is the realistic path for the power ICs. Full hand-iron on every fine-pitch pad is painful; one focused day with paste and airflow is enough for a first board.

---

## Parked idea: Raspberry Pi as the “brain”

Not replacing the P1 power test bed — only the MCU / software side if ESP32 firmware + SD feel too heavy.

### Architecture (two power domains)

| Side | Power | Role |
|------|--------|------|
| **This board** | Battery/USB → **bq25185** → **TPS61023** → **TPS26625** → RJ12 | Real **P1 5 V @ ~250 mA** so Ghost + charger/boost path can be tested |
| **Raspberry Pi 4 or 5** | Own wall PSU **or** Pi UPS HAT (battery) | Runs easy software (Python); drives Request / Data GPIO |

- BQ / boost / eFuse stay. They are **not** for the Pi.
- Pi is **not** fed from `VCC_3V3` or the small boost.
- Connect only **signals + shared GND** (headers / cable): GPIO → Data TX opto LED; Request opto → GPIO.
- Opto VCC still from board **SYS_5V**.
- On a Pi-only spin you can drop ESP32 + possibly SY8088; keep P1 power path.

### Pi battery (EU shops)

Pi itself has no built-in battery. Buy Pi + UPS HAT, e.g.:

- [Kubii — SunFounder PiPower 5](https://www.kubii.com/en/poe-hat-tarjetas-de-expansion/5160-pipower-5-hats-for-raspberry-pi-3272496326866.html) (FR/EU)
- Amazon.nl / Amazon.de — Geekworm X120x UPS for Pi 5
- Kiwi Electronics (NL), BerryBase (DE), Nettigo (PL)

That UPS powers **only the Pi**. Board battery path stays for P1 / Ghost tests.

### When to use this idea

- Lab / desk: want Python + large telegram files, less C++ pain.
- Portable field Ghost range test: prefer **ESP32** on this board (Pi is bulkier and its UPS is a second power system).

Decision later — ESP32 remains the default locked design until explicitly changed.
