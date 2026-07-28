# Smart Meter Simulator — Architecture & Design Guide

**Goal:** Portable **DSMR P1 meter-side** board so you can develop and field-test **P1 Ghost** (Wi‑Fi range, etc.) without asking to use real doorstep meters.

**MCU:** ESP32-C3-MINI-1 (Wi‑Fi **on** for config / OTA / talk-to-device)  
**Power:** Seeed **Lipo Rider Plus** daughterboard → **5 V only** + **on-board 5→3.3 V** (≥500 mA)  
**P1 +5 V:** TI **TPS2662** foldback  
**Store:** **microSD** telegram files (not SDRAM, not live Wi‑Fi fetch as primary)  
**Connector:** RJ12 6P6C female (meter side)  
**Signals:** Optocouplers on Request + Data (DSMR-like); optional isolated DC-DC for true floating P1  
**Volume:** ~5 boards — cost of SD / OLED / optos is fine  
**Skip:** LoRa  

Part picking: **[PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)**  
Mechanicals: `mechanicals/lipo_rider_plus/`

---

## 1. What this board is (and is not)

| Role | Device | RJ12 side |
|------|--------|-----------|
| **This project (Simulator)** | Acts as the **meter** | Female jack, **supplies** +5V, **senses** Data Request, **drives** Data (OC / opto) |
| P1 Ghost / OSM | Acts as the **reader** | Male plug, **takes** +5V, **drives** Data Request high, **reads** Data |

**Field use:** battery + simulator in a building corner → Ghost on RJ12 → you elsewhere with a laptop checking **Ghost** Wi‑Fi. Simulator replays telegrams from **microSD**.

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
│                     SMART METER SIMULATOR PCB                            │
│                                                                          │
│  Lipo Rider Plus ──5V──► SYS_5V                                          │
│  (USB-C + LiPo)            │                                             │
│                            ├─► 5V→3.3V (≥500 mA) ──► VCC_3V3 ──► ESP32   │
│                            │                         │         + microSD │
│                            │                         │         ± OLED    │
│                            └─► TPS2662 ──► P1_5V ──► RJ12 pin1           │
│                                 (± iso DC-DC if full isolation)          │
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
| 3 | Lipo Rider Plus headers (5V/GND/EN) | **Required** — buy module |
| 4 | On-board **5V→3.3V** (≥500 mA) | **Required** — Rider 3V3 is only 250 mA |
| 5 | **TPS2662** SYS_5V→P1_5V | **Required** — DSMR foldback |
| 6 | RJ12 6P6C | **Required** |
| 7 | Request path (opto) | **Required** |
| 8 | Data path (opto / OC) | **Required** |
| 9 | microSD | **Required** — telegram store |
| 10 | ESD USB + RJ12 | **Required** |
| 11 | LED + button | **Recommended** |
| 12 | OLED | **Optional** — handy in the field |
| 13 | Isolated 5V DC-DC | **Optional** — needed only for true floating P1 GND |
| 14 | LoRa | **Skip** |
| 15 | Rider 3V3 → ESP32 | **Skip** |

---

## 3. Important rules

### 3.1 Power budgets

| Rail | Source | Budget |
|------|--------|--------|
| `SYS_5V` | Lipo Rider 5V | Up to **2.4 A** available; you need ≪ that |
| `P1_5V` | TPS2662 | ~**250 mA** continuous, foldback on fault (DSMR) |
| `VCC_3V3` | On-board regulator | Size **≥500 mA** (Wi‑Fi + SD + OLED) |

**Do not** power the ESP32 from Lipo Rider **3V3** (spec **250 mA**).

### 3.2 P1 +5V foldback

DSMR: ~250 mA continuous, overload ~260–300 mA, then **foldback** (ISC ≤ 50 mA).  
Implement with **TPS2662** ([slvaf94](https://www.ti.com/lit/pdf/slvaf94)).

### 3.3 Data Request polarity

- OSM sets pin 2 **HIGH (~5 V)** → start sending  
- OSM **releases** high‑Z to stop (must **not** drive hard to GND)  
- MCU only **senses** (via opto); never drives pin 2  

### 3.4 Data line = open-collector + inverted UART

- Meter drives pin 5 open-collector / open-drain (opto output stage)  
- Idle pulled high by OSM (1–10 kΩ)  
- 115200 8N1; watch firmware invert vs hardware invert  

Use **high-speed** optos (TLP2361 / 6N137 / digital isolator). **PC817 is often too slow** at 115200.

### 3.5 Isolation

Real meters isolate P1 from mains. This board has no mains.

- **In scope:** optos on Request + Data (DSMR-like)  
- **True galvanic split:** add isolated 5V DC-DC + `GND_ISO` on RJ12  
- USB D+/D− still need a ground reference to the PC when flashing (shared MCU GND, or a USB isolator)

### 3.6 Storage & Wi‑Fi roles

| Path | Role |
|------|------|
| **microSD** | Primary telegram library in the field |
| **Wi‑Fi** | Talk to device / OTA / config — **not** the main telegram pipe |
| **USB-C** | First flash + serial debug |
| Internal flash | Optional small cache; SD is the library |

---

## 4. RJ12 pin map (meter / simulator)

| Pin | Name | Simulator must… |
|-----|------|------------------|
| 1 | +5V | **Source** 5 V, current-limited (~250 mA) |
| 2 | Data Request | **Sense** HIGH → enable TX |
| 3 | Data GND | System GND or `GND_ISO` |
| 4 | NC | Leave open |
| 5 | Data | **OC / opto** UART from MCU TX |
| 6 | Power GND | Same as pin 3 |

Official: [P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)

---

## 5. Reference circuit patterns

### 5.1 Power

```
Lipo Rider 5V ──► SYS_5V
                    ├─► 5→3.3 regulator ──► VCC_3V3 ──► ESP32, SD, OLED
                    └─► TPS2662 ──► P1_5V ──► (± iso DC-DC) ──► RJ12 pin1
```

Leave Rider **3V3** pin unconnected (or mark DNP test only).

### 5.2 Request (opto)

```
RJ12 pin2 ──► opto LED (+ series R to P1_5V or from OSM drive)
opto transistor / digital out ──► ESP32 GPIO (3.3 V domain)
```

Document active level in firmware.

### 5.3 Data (opto OC)

```
ESP32 UART TX ──► opto LED (3.3 V domain)
opto output (OC) ──► RJ12 pin5
Optional 4.7 kΩ pin5 → P1_5V for bench
```

Match invert in HW/SW once; do not double-invert.

### 5.4 USB-C data

- CC: 5.1 kΩ on CC1/CC2  
- ESD: USBLC6-2SC6 on D+/D−  
- ESP32-C3: **GPIO18 = D−, GPIO19 = D+**  

### 5.5 microSD

SPI mode is simplest on C3: CS, MOSI, MISO, SCK + card detect optional.  
Store plain DSMR `.txt` telegrams; firmware rotates / selects via button or Wi‑Fi UI.

---

## 6. Suggested ESP32-C3 pin assignment

| GPIO | Function | Notes |
|------|----------|--------|
| 18 / 19 | USB D− / D+ | Fixed |
| Free UART TX | → Data opto LED | Prefer free UART |
| Free GPIO in | Request after opto | Not a strap pin |
| SPI pins | microSD | Avoid straps |
| I²C (optional) | OLED | SDA/SCL |
| Free GPIO | LED / button | Avoid boot straps |
| EN | Reset | RC network |

---

## 7. Day-by-day / KiCad order

Work **one subcircuit** at a time. End with: schematic snippet + PN + how to test.

| Step | Subcircuit | Done when… |
|------|------------|------------|
| 1 | Nets + Lipo Rider header | `SYS_5V`, `VCC_3V3`, `P1_5V`, `P1_REQ`, `P1_DATA`, `GND` |
| 2 | 5→3.3 | ESP32 can run from SYS_5V path |
| 3 | Board USB-C | CC + ESD; D+/D− to 18/19 |
| 4 | ESP32-C3-MINI-1 | Flash blink over USB |
| 5 | microSD | Mount FAT; read a file |
| 6 | TPS2662 | P1_5V ≈ 5 V; short → foldback |
| 7 | RJ12 footprint | Pins 1…6 silk correct |
| 8 | Request opto | 5 V on pin2 → GPIO active |
| 9 | Data opto / OC | Scope pin5 clean at 115200 |
| 10 | ESD + LED/button (± OLED) | Bring-up checklist green |
| 11 | Firmware | Replay SD telegram while Request high; Wi‑Fi UI optional |

---

## 8. Bring-up checklist

1. Rider → `SYS_5V` OK; `VCC_3V3` OK (**not** from Rider 3V3)  
2. Flash blink via board USB  
3. Wi‑Fi STA joins (smoke test)  
4. SD lists telegram files  
5. `P1_5V` ≈ 5 V; brief short pin1–GND → foldback, recovers  
6. Force Request → MCU sees enable  
7. Pull-up on pin5 → scope UART; Ghost receives valid telegram  
8. Battery-only run in a corner with Ghost attached  

---

## 9. Relation to P1 Ghost

| Signal | Ghost (reader) | This simulator (meter) |
|--------|----------------|-------------------------|
| Pin 1 +5V | Input | **Output** (TPS2662) |
| Pin 2 Request | MCU drives HIGH | **Sense** via opto |
| Pin 5 Data | Level-shift → UART RX | **OC / opto** from UART TX |
| Goal | Parse / forward / Wi‑Fi | Replay from SD; portable fake meter |

---

## References

1. [DSMR P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)  
2. [TI slvaf94 — TPS2662](https://www.ti.com/lit/pdf/slvaf94)  
3. [Seeed Lipo Rider Plus](https://wiki.seeedstudio.com/Lipo-Rider-Plus/)  
4. [PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)  
5. [arman087/P1_ghost](https://github.com/arman087/P1_ghost)  
