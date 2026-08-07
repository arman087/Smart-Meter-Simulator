# Parts checklist — big / hand-build

Work only in this folder’s KiCad project. Prefer **0603+ / SOT-223 / DIP / SOIC** where possible.

**Legend:** 🔧 on PCB · 🔌 module / kit · ○ optional

---

## Modular

| # | Item | Example | Status |
|---|------|---------|--------|
| M1 | USB-C **data** | Breakout → ESP32 D+/D− | 🔌 |
| M2 | microSD | SPI breakout, 2.54 mm headers | 🔌 |
| M3 | MCU | ESP32-C3 **DevKit** headers **or** MINI-1 module | 🔌 |

---

## Power on PCB

| # | Item | Candidate | Notes | Status |
|---|------|-----------|-------|--------|
| P1 | LiPo charger | bq25185 / similar with terminate + UVLO | Hot air/oven OK | 🔧 |
| P2 | Charge USB-C | On-PCB receptacle + CC 5.1 kΩ | Separate from data USB | 🔧 |
| P3 | Battery | 1S LiPo, JST or pads | | 🔧 |
| P4 | 5 V boost | ~2 A class discrete (not MT3608 junk) | Layout critical | 🔧 |
| P5 | 5→3.3 V | **AMS1117-3.3 SOT-223** (or LM1117) | From `SYS_5V` | 🔧 |
| P6 | P1 limit | **TPS2553DBVR** | RILIM ≈ 250–300 mA | 🔧 |
| P7 | P1 current | **INA226** or **INA219** | After TPS2553; I²C | 🔧 |

---

## P1 / isolation / UI

| # | Item | Candidate | Status |
|---|------|-----------|--------|
| S1 | RJ12 6P6C female | Meter jack | 🔧 |
| S2 | Request opto | **6N137** DIP-8 | 🔧 |
| S3 | Data opto | **6N137** DIP-8 | 🔧 |
| S4 | ESD | USB + RJ12 TVS | 🔧 |
| S5 | LED + button | Large tact + 0603/0805 LED | 🔧 |
| S6 | OLED | Optional I²C | ○ |

---

## Skip

| Item | Why |
|------|-----|
| SY8089AAC as final choice | SOT-23-5 too small for this path |
| Hall analog → GPIO5 | ESP32-C3 GPIO5 has no ADC |
| Modular charger/boost stacks | Everything power stays on PCB |
| TPS2662 requirement | Replaced by TPS2553 for hand-build lab use |

---

## Pin / GPIO notes (ESP32-C3)

- USB D−/D+ : IO18 / IO19 (from data USB module)  
- ADC only : GPIO0–4  
- INA I²C : any free GPIOs; **GPIO5 OK**  
- TPS2553 FAULT : free GPIO  
- SPI : SD module  

---

## Rough buy list

- [ ] Charger IC + charge USB-C + JST  
- [ ] Boost IC + inductor + ceramics  
- [ ] AMS1117-3.3 SOT-223  
- [ ] TPS2553DBVR + RILIM  
- [ ] INA226 or INA219  
- [ ] 6N137 ×2 DIP-8  
- [ ] RJ12 female  
- [ ] ESP32-C3 DevKit or MINI-1  
- [ ] USB-C data breakout  
- [ ] microSD breakout + card  
- [ ] LiPo 1S  
