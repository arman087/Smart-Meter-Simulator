# Architecture — big / hand-build direction

Active project folder: `my_design/Slimme_meter_Sim -big-modular/`  
Parent repo docs under `Smart Meter Simulator/` root are **frozen** for this path — edit here instead.

---

## Product

Portable DSMR **P1 meter-side** simulator for testing P1 Ghost (Wi‑Fi range, etc.) without a real meter.

- Female RJ12: source +5 V, sense Request, OC/opto Data  
- Telegrams from **microSD** (module)  
- Wi‑Fi on ESP32 for config / OTA (DevKit or module)

---

## Modular vs on-board

### Modular only

1. **USB-C data** breakout → ESP32 D+/D− (flash / CDC)  
2. **microSD** breakout → SPI  
3. **ESP32** — DevKit on headers **or** ESP32-C3-MINI-1 soldered module  

### Integrate on PCB (not modular)

1. Charge USB-C + **LiPo charger**  
2. **5 V boost** (battery / SYS → `SYS_5V`)  
3. **5→3.3** regulator (large footprint)  
4. **TPS2553** → `P1_5V`  
5. **INA219/226** current sense on P1 output  
6. **6N137** Request + Data  
7. RJ12, UI, ESD  

---

## Nets

```
VBAT          LiPo
SYS_5V        Boost output (+5 V board rail)
VCC_3V3       Regulator → ESP32
P1_5V         After TPS2553 (+ after shunt/INA)
P1_REQ        RJ12 pin2
P1_DATA       RJ12 pin5
I2C_SDA/SCL   INA (GPIO5 may be one of these)
```

---

## P1 current limit + measurement

```
SYS_5V ──► TPS2553 ──► sense (INA shunt) ──► RJ12 pin1
                │              │
             FAULT ── GPIO   I²C ── ESP32
```

- Limit: ~250–300 mA via TPS2553 `RILIM`  
- Measure: INA reports mA → firmware can show power ≈ 5 × I  
- Optional: FAULT pin when limit hit  
- **Do not** wire analog Hall to GPIO5 (not ADC on ESP32-C3)

TPS2553 = current **limit** (constant-current). Not full DSMR foldback to ≤50 mA (that was TPS2662). Acceptable for lab Ghost testing.

---

## Optocouplers

- **Data:** 6N137 DIP-8 (115200)  
- **Request:** 6N137 DIP-8 (or slower DIP OK)  

---

## What we skip on this path

- Full JLCPCB assembly of tiny QFN-only boards as the only option  
- Modular charger / boost / opto “stacks”  
- SY8089AAC as final 3.3 V (too small) — use SOT-223 class  
- LoRa  
- Analog Hall on GPIO5  

---

## Suggested work order in KiCad (this folder)

1. Power sheet: charger + boost → `SYS_5V`  
2. 3.3 V + TPS2553 + INA → `P1_5V`  
3. Headers for ESP32 DevKit / module, USB-C data module, SD module  
4. RJ12 + 6N137 ×2  
5. UI + ESD  
6. ERC / hand-solder BOM (large packages preferred)
