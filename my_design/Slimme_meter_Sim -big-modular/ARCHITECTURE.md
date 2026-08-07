# Architecture — DevKit + slim P1 carrier

## Locked direction

1. **Brain:** SparkFun **Thing Plus ESP32-S3** (or equal premium S3 board with USB-C + SD + headers).  
2. **Carrier PCB:** P1 electrical interface only — powered from DevKit **`V_USB` / 5 V header** (and optionally `VBAT` boost).

Parent `Smart Meter Simulator/` root docs stay untouched.

---

## Block diagram

```
┌─────────────────────────────────────┐
│  SparkFun Thing Plus ESP32-S3       │
│  USB-C · LiPo · SD · 3V3 · Wi‑Fi    │
│  Headers: V_USB, 3V3, VBAT, GPIO    │
└──────────────┬──────────────────────┘
               │ V_USB (5V*) · GPIOs · GND · (VBAT)
               ▼
┌─────────────────────────────────────┐
│  Slim P1 carrier (your KiCad)       │
│  TPS2553 → INA → RJ12 pin1          │
│  6N137 Request / Data               │
│  RJ12 · ESD · optional VBAT→5V boost│
└─────────────────────────────────────┘
* 5 V on V_USB when USB-C powered; see README for battery-only.
```

---

## Slim PCB contents

| Block | Part | Notes |
|-------|------|--------|
| Input | Feather/Thing Plus female headers | Mechanically stack or cable |
| P1 5 V limit | **TPS2553** | ~250–300 mA |
| Current sense | **INA226** / **INA219** | After eFuse |
| Optos | **6N137** DIP-8 ×2 | Request + Data |
| Connector | RJ12 6P6C female | Meter side |
| Optional | Boost VBAT→5 V | Battery-only P1 power |
| Optional | LED / button | Status |

---

## DevKit responsibilities

| Need | Thing Plus |
|------|------------|
| MCU + Wi‑Fi | ESP32-S3 |
| Flash / serial | USB-C |
| Telegram files | microSD |
| Charge LiPo | On-board MCP73831 + gauge |
| 3.3 V for MCU | On-board regulator |
| Feed carrier | `V_USB` pin ≈ 5 V (USB present) |

---

## Pin plan (starter — confirm against Thing Plus pinout)

| Function | DevKit side |
|----------|-------------|
| GND | GND |
| 5 V to carrier | **V_USB** |
| Optional boost in | **VBAT** |
| UART TX → Data opto | Free UART TX |
| Request GPIO | Free input |
| I²C SDA/SCL | INA (Qwiic possible if wiring matches) |
| FAULT | Free GPIO |

Use SparkFun’s pinout PDF when assigning exact numbers:  
https://docs.sparkfun.com/SparkFun_Thing_Plus_ESP32-S3/

---

## KiCad work order (this folder)

1. Thing Plus / Feather **header footprint** + silk  
2. `V_USB` → TPS2553 → INA → RJ12 pin1  
3. Optos + RJ12 pins 2 & 5  
4. Optional VBAT boost for battery-only 5 V  
5. ESD + test points  
6. Stack height / mounting holes matching Thing Plus  

Schematics already in tree (`SCH_1_*`, `SCH_2_*`) can be stripped down to this slim carrier.
