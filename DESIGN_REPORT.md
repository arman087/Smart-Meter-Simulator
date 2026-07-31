# Smart Meter Simulator — Design report

**Status:** Power path through **TPS61023 → SYS_5V** is drawn in KiCad.  
**Working project:** `my_design/Slimme_meter_Sim/` (sheet `SCH_1_USB_5volt_sch`)  
**Date of this milestone:** July 2026

This note records **why** the board exists, **what** was decided, and **how** the first power sheet was built — so the design can be reviewed without guessing from the schematic alone.

---

## 1. Why this board exists

[P1 Ghost](https://github.com/arman087/P1_ghost) is a DSMR **P1 reader**. Developing and field-testing it against real doorstep meters is awkward: access, permission, and fixed locations.

The Smart Meter Simulator is the **meter side** of the RJ12 link:

| Role | Device |
|------|--------|
| This board | Meter: female RJ12, **sources** +5 V, **senses** Data Request, **drives** Data |
| P1 Ghost / OSM | Reader: male RJ12, takes +5 V, drives Request, reads Data |

Typical use: battery-powered simulator in a building corner → Ghost on the cable → develop Ghost Wi‑Fi / range elsewhere. Telegrams come from **microSD**, not from a live meter.

Official behaviour follows the [DSMR P1 Companion Standard](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf) (115200 8N1, Request / Data / +5 V pin map, ~250 mA continuous on pin 1 with foldback on overload).

---

## 2. What we need from the power system

Three consumers share one portable board:

1. **ESP32-C3 + microSD (± OLED)** — need a solid **3.3 V**, ≥ **500 mA** headroom for Wi‑Fi bursts.  
2. **P1 port (RJ12 pin 1)** — must look like a real meter: regulated **~5 V**, current-limited with **foldback** (~250 mA continuous).  
3. **1S LiPo** — charge from USB when docked; run from battery in the field.

That forces a clear rail hierarchy:

```
USB-C ──► charger / power-path ──► VSYS (cell or ~4.5 V) ──► boost ──► SYS_5V (+5 V)
                                        │                              │
                                     LiPo                   ┌──────────┴──────────┐
                                                            ▼                     ▼
                                                     5 V → 3.3 V            eFuse / foldback
                                                            ▼                     ▼
                                                       VCC_3V3                 P1_5V → RJ12
```

**SYS_5V is the hub.** Both the MCU regulator and the P1 path take power from the boosted 5 V rail — not from the raw system / battery node.

---

## 3. Decisions that shaped the architecture

### 3.1 One PCB, not a power daughterboard

An early idea was a commercial USB / LiPo “rider” board stacked under the simulator. That was dropped:

- Extra connectors and mechanical stack for only ~5 boards  
- Harder to own the exact rails (true 5 V for P1, ≥500 mA for 3.3 V)  
- Charge / boost / MCU USB data want to live on **one** layout we control  

So charge, boost, MCU, SD, and RJ12 all go on the **main PCB**.

### 3.2 Charger: TI bq25185

Chosen for a compact **1S** design with:

- USB charge input and power-path so the board can run while charging  
- Battery undervoltage lockout (2-wire LiPo is enough)  
- Practical charge / input current around **1 A** — enough for ~250 mA P1 load plus a realistic 3.3 V budget  

**Important:** charger system pin **VSYS** (net `V+` in the schematic) is **not** 5 V. With USB it sits near ~4.5 V; on battery it tracks the cell (~3.0–4.2 V). That rail is only an intermediate supply for the boost.

### 3.3 Boost: TI TPS61023 → SYS_5V

Required, not optional:

| If we skip the boost… | What breaks |
|------------------------|-------------|
| Feed RJ12 from VSYS | Ghost sees ~3–4 V on battery — not a DSMR-like P1 supply |
| Run a 3.3 V LDO from VSYS alone | No headroom when the cell is low → brown-out under Wi‑Fi |

TPS61023 takes VSYS and makes a fixed **+5 V** (`SYS_5V`). Feedback resistors were picked for 5.0 V (FB stack **732 kΩ / 100 kΩ**). Inductor **1 µH** class for this boost; bulk ceramics next to charger and boost per TI layout practice.

### 3.4 P1 current limit: TI TPS2662 (next sheet)

DSMR expects pin 1 to supply ~**250 mA** continuously and then **fold back** on overload — not only a hard trip. TI documents this use case for smart-meter user ports ([slvaf94](https://www.ti.com/lit/pdf/slvaf94)). That block sits **after** SYS_5V and is not drawn yet on the first sheet.

### 3.5 MCU and storage

| Choice | Reason |
|--------|--------|
| **ESP32-C3-MINI-1** | Small module, native USB, Wi‑Fi for config / OTA |
| **microSD** | Primary telegram library (Wi‑Fi is not the main store) |
| **No LoRa on simulator** | Out of scope; Ghost carries the radio story |

### 3.6 USB-C

Charge / power USB-C on the first sheet: JLCPCB / LCSC **C165948** (TYPE-C-31-M-12), 5.1 kΩ on CC for sink, D+/D− reserved for ESP32 GPIO18/19 when the MCU sheet lands. Charge current is set with ISET; a small slide switch parallels a second ISET resistor so the board can select ~**500 mA** or ~**1 A** charge without resoldering.

---

## 4. How the first sheet was built

KiCad project: **`my_design/Slimme_meter_Sim/`**  
Sheet: **`SCH_1_USB_5volt_sch.kicad_sch`**

### Done on this milestone

1. USB-C receptacle, CC resistors, input path into **bq25185**  
2. Battery **JST-PH** (S2B-PH-SM4-TB style), charge / status LEDs (CHG / FAULT / 5 V present)  
3. VSET / ILIM and ISET resistor network (including charge-current switch)  
4. **TPS61023** boost with inductor, FB divider, input/output ceramics  
5. Net **SYS_5V** as the feed for the next two supplies (3.3 V regulator + P1 eFuse)

Parts were chosen for **JLCPCB / LCSC** assembly where possible (0402/0603/0805/1206 passives, EasyEDA-exported footprints and 3D models under the project).

### Intentionally not on this sheet yet

- 5 V → 3.3 V regulator (`VCC_3V3`)  
- TPS2662 → `P1_5V` → RJ12  
- ESP32-C3, microSD, Request / Data optos, ESD, UI  

That matches the planned order: finish a measurable **5 V hub**, then hang MCU and P1 off it.

### Quick bring-up targets for sheet 1

1. USB plugged in → battery charges; CHG behaviour sane  
2. `V+` / VSYS present (~4.5 V on USB, tracks cell on battery)  
3. `SYS_5V` ≈ **5.0 V** on USB **and** on battery-only  

---

## 5. Power budget (design intent)

| Rail | Source | Intent |
|------|--------|--------|
| VSYS / `V+` | bq25185 | Intermediate only |
| `SYS_5V` | TPS61023 | Board 5 V hub (~1 A class IC; real load ≪ that) |
| `P1_5V` | TPS2662 from SYS_5V | ~250 mA continuous, foldback on fault |
| `VCC_3V3` | 5→3.3 from SYS_5V | ≥500 mA for Wi‑Fi |

Ghost on a 250 mA P1 budget: LoRa-only TX is comfortable; Wi‑Fi-only is tight; Wi‑Fi + LoRa TX together may need battery assist or mutually exclusive TX — that is a Ghost firmware constraint, not a reason to raise the meter pin above DSMR.

---

## 6. What “done so far” means

| Area | State |
|------|--------|
| Problem / product role | Locked |
| Rail architecture (VSYS → SYS_5V → 3V3 + P1) | Locked |
| KiCad: USB → charge → boost → **5 V** | **Drawn** |
| KiCad: 3.3 V, TPS2662, RJ12, MCU, SD, optos | Next |
| Firmware / telegram player | Later |

---

## 7. References (normative / silicon)

1. [DSMR P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf) — Netbeheer Nederland  
2. [TI bq25185 datasheet](https://www.ti.com/product/BQ25185) — charge + power path  
3. [TI TPS61023 datasheet](https://www.ti.com/product/TPS61023) — VSYS → 5 V boost  
4. [TI slvaf94](https://www.ti.com/lit/pdf/slvaf94) — foldback on smart-meter user ports (TPS2662)  
5. [arman087/P1_ghost](https://github.com/arman087/P1_ghost) — reader under test  

Architecture checklist and KiCad order: [DESIGN_GUIDE.md](DESIGN_GUIDE.md) · Parts: [PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)
