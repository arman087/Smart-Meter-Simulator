# Smart Meter Simulator — Architecture & Design Guide

**Goal:** Portable **DSMR P1 meter-side** board so you can develop and field-test **P1 Ghost** (Wi‑Fi range, etc.) without asking to use real doorstep meters.

**MCU:** ESP32-C3-MINI-1 (Wi‑Fi **on** for config / OTA / talk-to-device)  
**Power (on main PCB):** **bq25185** (charge + `VSYS`/`V+`) + **TPS61023** (`V+` → **+5 V**) + **on-board 5→3.3 V** (≥500 mA)  
**P1 +5 V:** TI **TPS2662** foldback  
**Store:** **microSD** telegram files  
**Connector:** RJ12 6P6C female (meter side)  
**Signals:** Optocouplers on Request + Data; optional isolated DC-DC for true floating P1  
**Volume:** ~5 boards  
**Skip:** LoRa · feeding RJ12 from `V+` without the boost  

Part picking: **[PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)**  
Design story: **[DESIGN_REPORT.md](DESIGN_REPORT.md)**  
KiCad: `my_design/Slimme_meter_Sim/`

---

## 1. What this board is (and is not)

| Role | Device | RJ12 side |
|------|--------|-----------|
| **This project (Simulator)** | Acts as the **meter** | Female jack, **supplies** +5V, **senses** Data Request, **drives** Data (OC / opto) |
| P1 Ghost / OSM | Acts as the **reader** | Male plug, **takes** +5V, **drives** Data Request high, **reads** Data |

**Field use:** battery + simulator in a building corner → Ghost on RJ12 → you elsewhere checking **Ghost** Wi‑Fi. Simulator replays telegrams from **microSD**.

```
microSD telegrams ──► ESP32-C3 ──► opto / OC UART ──► RJ12 pin5 (Data)
                         ▲                               │
                    Request ◄── opto ◄── RJ12 pin2 ◄── Ghost
                         │
              SYS_5V ── TPS2662 ──► RJ12 pin1 ──► powers Ghost
```

---

## 2. Architecture (locked)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     SMART METER SIMULATOR PCB (one board)                │
│                                                                          │
│  USB-C ──► bq25185 ──► VSYS/V+ (3.0–4.5 V) ──► TPS61023 ──► SYS_5V     │
│                 │                              │                         │
│              LiPo JST           ┌──────────────┴──────────────┐          │
│                                 ▼                             ▼          │
│                          5V→3.3V (≥500 mA)              TPS2662          │
│                                 ▼                             ▼          │
│                            VCC_3V3 ── ESP32              P1_5V → RJ12    │
│                                   + microSD ± OLED                       │
│                                                                          │
│  Board USB-C (D+/D−) ─────────────────────────────► ESP32 flash         │
│  RJ12 pin2 ──► Request opto ──► GPIO                                     │
│  ESP32 TX ──► Data opto / OC ──► RJ12 pin5                               │
└──────────────────────────────────────────────────────────────────────────┘
```

### Block checklist

| # | Block | Verdict |
|---|--------|---------|
| 1 | Board USB-C (D+/D− flash) | **Required** |
| 2 | ESP32-C3-MINI-1 + EN / caps | **Required** |
| 3 | **bq25185** charge + power path | **Required** |
| 4 | **TPS61023** `V+` → `SYS_5V` | **Required** — do **not** omit |
| 5 | On-board **5V→3.3V** (≥500 mA) | **Required** |
| 6 | **TPS2662** SYS_5V→P1_5V | **Required** — DSMR foldback |
| 7 | RJ12 6P6C | **Required** |
| 8 | Request + Data optos | **Required** |
| 9 | microSD | **Required** |
| 10 | ESD USB + RJ12 | **Required** |
| 11 | LED + button | **Recommended** |
| 12 | OLED | **Optional** |
| 13 | Isolated 5V DC-DC | **Optional** — true floating P1 |
| 14 | LoRa | **Skip** |
| 15 | Skip TPS61023 / use `V+` as P1 5 V | **Skip — wrong** |

---

## 3. Important rules

### 3.1 What `VSYS` / `V+` is (bq25185 pin 1)

Charger **VSYS** (schematic net `V+`) is **not** a 5 V rail.

| Condition | Typical voltage |
|-----------|-----------------|
| USB / DC in | ~**4.5 V** regulated |
| Battery only | ~**3.0–4.2 V** (follows cell) |

**TPS61023** boosts `V+` → fixed **+5 V** (`SYS_5V`). Keep it so:

- RJ12 / Ghost always see real ~5 V on battery  
- Your 5→3.3 regulator always has headroom (LDO from a 3.2 V cell cannot make 3.3 V)

### 3.2 Power budgets

| Rail | Source | Budget |
|------|--------|--------|
| `V+` / VSYS | bq25185 | Intermediate only |
| `SYS_5V` | TPS61023 | ~**1 A** class IC; board load ≪ that |
| `P1_5V` | TPS2662 | ~**250 mA** continuous, foldback on fault |
| `VCC_3V3` | On-board regulator from `SYS_5V` | **≥500 mA** |

### 3.3 P1 +5V foldback

DSMR: ~250 mA continuous, overload ~260–300 mA, then **foldback**.  
**TPS2662** — [slvaf94](https://www.ti.com/lit/pdf/slvaf94).

### 3.4 Data Request / Data

- Pin 2 HIGH (~5 V) → start TX; release high‑Z to stop  
- Pin 5 open-collector / opto; 115200 8N1; use **fast** optos (not PC817)

### 3.5 Isolation

Optos in scope. True floating P1 needs isolated 5 V DC-DC + `GND_ISO`.

### 3.6 Storage & Wi‑Fi

| Path | Role |
|------|------|
| **microSD** | Primary telegram library |
| **Wi‑Fi** | Config / OTA — not primary telegram pipe |
| **USB-C** | First flash + serial |

---

## 4. RJ12 pin map (meter / simulator)

| Pin | Name | Simulator must… |
|-----|------|------------------|
| 1 | +5V | **Source** 5 V via TPS2662 |
| 2 | Data Request | **Sense** HIGH → enable TX |
| 3 | Data GND | System GND or `GND_ISO` |
| 4 | NC | Leave open |
| 5 | Data | **OC / opto** UART from MCU TX |
| 6 | Power GND | Same as pin 3 |

---

## 5. Reference circuit patterns

### 5.1 Power (main PCB)

```
USB-C ──► bq25185 ──► V+ / VSYS
              │            │
           VBAT/LiPo       └──► TPS61023 ──► SYS_5V
                                              ├─► 5→3.3 ──► VCC_3V3
                                              └─► TPS2662 ──► P1_5V ──► RJ12 pin1
```

Keep **both** charger and boost. Omit unused solar / DC terminal pads if not needed.

### 5.2–5.5

Request opto, Data opto OC, USB-C data (GPIO18/19), microSD SPI — see circuit NOTES and earlier patterns in `circuits/`.

---

## 6. Suggested ESP32-C3 pin assignment

| GPIO | Function |
|------|----------|
| 18 / 19 | USB D− / D+ |
| Free UART TX | → Data opto |
| Free GPIO in | Request after opto |
| SPI | microSD |
| I²C optional | OLED |
| Free GPIO | LED / button |
| EN | Reset RC |

---

## 7. KiCad order

| Step | Subcircuit | Done when… |
|------|------------|------------|
| 1 | Nets + bq25185 + TPS61023 (`02`) | `V+`, `SYS_5V`, charge, battery — **in progress in Slimme_meter_Sim** |
| 2 | 5→3.3 (`03`) | `VCC_3V3` stable under Wi‑Fi |
| 3 | Board USB-C (`01`) | Flash blink |
| 4 | ESP32 (`05`) | CDC + Wi‑Fi smoke |
| 5 | microSD (`12`) | Read telegram file |
| 6 | TPS2662 (`04`) | P1_5V; short → foldback |
| 7 | RJ12 + optos (`06`/`11`/`07`/`08`) | Ghost gets valid telegram |
| 8 | ESD + UI (`09`/`10`) | Bring-up checklist green |

---

## 8. Bring-up checklist

1. Charge USB → battery charges; `V+` present  
2. `SYS_5V` ≈ 5 V (boost on); battery-only still ≈ 5 V  
3. `VCC_3V3` ≈ 3.3 V; Wi‑Fi without brown-out  
4. Flash via board USB; SD lists files  
5. `P1_5V` ≈ 5 V; short → foldback, recovers  
6. Request → TX; Ghost receives telegram  

---

## 9. Relation to P1 Ghost

| Signal | Ghost | Simulator |
|--------|-------|-----------|
| Pin 1 +5V | Input | **Output** (TPS2662) |
| Pin 2 Request | Drives HIGH | **Sense** via opto |
| Pin 5 Data | UART RX path | **OC / opto** from TX |

---

## References

1. [DSMR P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)  
2. [TI slvaf94 — TPS2662](https://www.ti.com/lit/pdf/slvaf94)  
3. [TI bq25185](https://www.ti.com/product/BQ25185) · [TI TPS61023](https://www.ti.com/product/TPS61023)  
4. [PARTS_CHECKLIST.md](PARTS_CHECKLIST.md) · [DESIGN_REPORT.md](DESIGN_REPORT.md)  
5. [arman087/P1_ghost](https://github.com/arman087/P1_ghost)  
