# Slimme meter Sim — DevKit brain + slim P1 board

**Active path:** this folder only.

## Idea

Use a **premium ESP32-S3 development board** that already has USB-C, microSD, 3.3 V regulation, and (ideally) LiPo charge.  
Your custom PCB is **only the P1 meter front-end**: take **5 V from the DevKit headers** → eFuse → RJ12 + optos (+ current sense).

## Recommended DevKit

**[SparkFun Thing Plus — ESP32-S3](https://www.sparkfun.com/sparkfun-thing-plus-esp32-s3.html)** (Feather / Thing Plus footprint)

| Built-in | You get |
|----------|---------|
| ESP32-S3 | Wi‑Fi, strong MCU, PSRAM/flash options |
| USB-C | Power + programming |
| microSD | Telegram store (no SD module on your PCB) |
| 3.3 V regulator | Powers the S3 |
| LiPo JST + charger + fuel gauge | Portable brain |
| Headers | **`V_USB` (5 V)**, `3V3`, `VBAT`, GPIOs, Qwiic |

Docs: https://docs.sparkfun.com/SparkFun_Thing_Plus_ESP32-S3/

**Alt:** Adafruit Feather ESP32-S3 (excellent, LiPo, USB pin) — **no on-board SD** (needs Adalogger / extra).

## Split

| SparkFun Thing Plus (buy) | Your slim PCB (design) |
|---------------------------|-------------------------|
| ESP32-S3, USB-C, SD, LiPo charge, 3.3 V | Header footprint matching Thing Plus / Feather |
| | **`V_USB` → TPS2553 → INA → RJ12 pin1** |
| | Optos **6N137** Request + Data |
| | RJ12, ESD, LED/button optional |
| | Optional: small **VBAT→5 V boost** if you need P1 5 V on battery-only |

```
Thing Plus USB-C / LiPo
        │
        ├─ 3V3, MCU, SD, Wi‑Fi          (on DevKit)
        │
        └─ V_USB (5 V when USB present) ──► slim PCB
                                              TPS2553 ──► INA ──► RJ12 pin1
                                              optos ◄──► GPIO from DevKit headers
```

## Important: 5 V on battery-only

On Thing Plus / Feather-class boards, **`V_USB` is ~5 V mainly when USB-C is plugged in**.  
On **battery alone** you usually have **`VBAT` (~3.0–4.2 V)** and **3.3 V** — **not** a boosted 5 V rail.

So:

| Mode | P1 +5 V |
|------|---------|
| USB-C plugged into Thing Plus | Use **`V_USB` → TPS2553** — works |
| Battery only (field corner) | Add a **small boost on the slim PCB**: `VBAT` → 5 V → TPS2553, **or** keep USB power bank into the DevKit |

For your “park in a building corner” use case, plan either a USB power bank into the Thing Plus, or one boost IC on the slim board from `VBAT`.

## What you no longer design on the slim board

- ESP32 / DevKit MCU  
- USB-C data (use DevKit’s)  
- microSD  
- Main 3.3 V for the MCU  
- (Optional) LiPo charger — already on Thing Plus  

## GPIO / sense

- INA219/226 on slim board → I²C to Thing Plus pins  
- TPS2553 FAULT → GPIO  
- Request / Data optos → UART + GPIO on headers  

Detail: [ARCHITECTURE.md](ARCHITECTURE.md) · [PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)
