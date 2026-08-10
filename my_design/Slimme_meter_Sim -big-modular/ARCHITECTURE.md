# Architecture — big modular hand-build

## Goal

Battery-powered **P1 meter simulator**: replay telegrams, power Ghost (~250 mA @ 5 V), Wi‑Fi for config/OTA. No LoRa. No power-bank dependence.

## Module map

```
┌─────────────────────────────────────────────────────────────┐
│ MAIN PCB (you solder hard bits + through-hole)              │
│  USB-C breakout ──► charger IC ──► LiPo                     │
│                    └─► VSYS ──► boost IC ──► 5V_SYS         │
│  5V_SYS ──► TPS2662 ─┬─ [SEL jumper/0Ω] ──► RJ12 pin1       │
│           ──► TPS2553┘                                      │
│  5V_SYS ── [SW] ──|>|──► header to DevKit "5V"              │
│  6N137×2 · RJ12 · ESD · (opt INA)                           │
│  headers → SD breakout · headers → DevKit GPIO/UART         │
└─────────────────────────────────────────────────────────────┘
         │                         │
         ▼                         ▼
   ESP32-S3-DevKitC-1-N32R16V  microSD breakout
   (WROOM-2 MCU module)        (SPI module)
```

## Locked MCU module

**ESP32-S3-DevKitC-1-N32R16V** = **ESP32-S3-WROOM-2-N32R16V**  
(alt: **N16R8V** = WROOM-2 16 MB flash + 8 MB PSRAM)

| Need | How DevKit provides it |
|------|------------------------|
| Pin access | Dual 2.54 mm headers (same as N8R8) |
| Memory | More flash/PSRAM than WROOM-1 — good for telegrams / buffers |
| 5 V → 3.3 V | Onboard LDO from `5V` pin **or** DevKit USB |
| Programming | DevKit USB (**switch OPEN**, not tied to charger) |
| Field power | Main `5V_SYS` via **switch + diode** into DevKit `5V` |

**WROOM-2 caveat:** **GPIO35, GPIO36, GPIO37** are used by Octal flash/PSRAM — **do not use** on the carrier (headers may still show them; leave unconnected).

Rejected for this path: CoreS3-as-brain, Thing Plus (no battery→5 V), Feather USB pin as VIN.

## Power path (correct)

```
[Main USB-C breakout] ──► charger VIN ──► battery / VSYS
                                              │
                                              ▼
                                           boost
                                              │
                                              ▼
                                           5V_SYS
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                          TPS2662       TPS2553     [SW]─|>|─► DevKit 5V
                              │             │
                              └─────[SEL]───┘──► P1 / RJ12 pin1
```

`SEL` = jumper, 0 Ω, or switch — **exactly one** eFuse output connected to RJ12.

### Forbidden loop

Do **not** OR DevKit `5V` / DevKit USB VBUS into charger VIN while also feeding DevKit from `5V_SYS`. That makes:

`battery → boost → “fake USB” → charger → battery`

### Programming vs run

| State | `5V_SYS→DevKit` switch | Who powers ESP |
|-------|------------------------|----------------|
| Flash / serial recovery | OPEN | DevKit USB |
| Battery or main USB charge | CLOSED | `5V_SYS` → diode → DevKit LDO |

After bring-up: charge only on main USB-C; talk over Wi‑Fi.

## What stays modular (avoid tiny soldering)

| Function | Form |
|----------|------|
| ESP32-S3 | DevKitC module |
| USB-C receptacle | Breakout → wire/header to charger VBUS/GND |
| microSD | Breakout → SPI to DevKit |

## What you hand-solder on main

| Block | Notes |
|-------|-------|
| Charger IC | Bigger package if available |
| Boost IC | Bigger package / generous pads |
| eFuse ×2 | **TPS2662** + **TPS2553**; jumper/0 Ω selects one path to RJ12 |
| Passives for those three | 0603/0805 preferred |
| 6N137 DIP | Socket or solder DIP |
| RJ12, ESD, switch, diode, headers | Through-hole friendly where possible |

## P1 / Ghost

| RJ12 | Role |
|------|------|
| Pin 1 | +5 V via eFuse (~250–300 mA limit) |
| Pin 2 | Request → opto → GPIO |
| Pin 5 | Data ← opto OC from UART TX |
| GND | Shared with system for v1 (full float = later / optional iso DC-DC) |

## eFuse dual footprint (locked)

| Path | Part | Role |
|------|------|------|
| A | **TPS2662** | Foldback / preferred if solder OK |
| B | **TPS2553** | Fallback current limit if A fails or is DNP |

Bring-up: attempt A → if good, `SEL` = A. If bridges/shorts/skip, `SEL` = B.

Ghost works on either; foldback is nicer, not mandatory.
