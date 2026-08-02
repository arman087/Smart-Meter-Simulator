# Parts checklist — choose in KiCad / DigiKey / JLCPCB

Use this while picking footprints and filling the schematic.  
Architecture is locked in [DESIGN_GUIDE.md](DESIGN_GUIDE.md) and [README.md](README.md).

**Legend:** ✅ buy / pick now · 🔧 design on PCB · ○ optional · ✗ skip

---

## A. Power (integrate on main PCB)

| # | Item | Example | Notes | Status |
|---|------|---------|-------|--------|
| A1 | Charger IC | **bq25185** | USB charge, power path, BUVLO | 🔧 |
| A2 | 5 V boost | **TPS61023** + 1 µH + FB | Boosts `V+`/`VSYS` → `SYS_5V`. **Do not omit** | 🔧 |
| A3 | Charge USB-C | e.g. LCSC C165948 | CC 5.1 kΩ; optional share data with ESP32 | 🔧 |
| A4 | Battery connector | JST-PH or pads for 2-wire LiPo | bq25185 manages charge + UVLO | ✅ |
| A5 | 1S LiPo | 1000–3000 mAh | 2-wire OK | ✅ |
| A6 | microSD card | 8–32 GB, FAT32 | Telegram library | ✅ |

Working schematic: `my_design/Slimme_meter_Sim/` · Story: [DESIGN_REPORT.md](DESIGN_REPORT.md)

**Nets:** `VBUS` → bq25185 → `V+`/`VSYS` (3.0–4.5 V) → TPS61023 → `SYS_5V` (+5 V)

### A7 — Selectable charge current (bq25185 ISET)

**You want:** **250 / 500 / 1000 mA**, only **one** path on at a time.  
That means **one** 3-channel selector (SP3T) or **one** jumper — not three switches.

Formula: **ICHG ≈ 300 / RISET**. Use **±1%** resistors.

| Target ICHG | RISET | Part (1%) | LCSC |
|-------------|-------|-----------|------|
| **250 mA** | **1.20 kΩ** | 1200 Ω | search `1200R 1% 0603` |
| **500 mA** | **604 Ω** | 604 Ω | [C32183](https://www.lcsc.com/product-detail/C32183.html) |
| **1000 mA** | **301 Ω** | 301 Ω | search `301R 1% 0603` |

#### Option A — one SP3T slide (recommended)

**One** switch, three throws, hardware guarantees only one channel:

| Part | LCSC |
|------|------|
| **SHOU HAN MSK13C02** (SP3T) | **[C2681567](https://www.lcsc.com/product-detail/C2681567.html)** |

```
                    ┌── throw1 ── 1.20 kΩ ── GND   → 250 mA
  ISET ── COM ──────┼── throw2 ── 604 Ω   ── GND   → 500 mA
                    └── throw3 ── 301 Ω   ── GND   → 1000 mA
```

Silk: `0.25A / 0.5A / 1A`.

#### Option B — 1×3 header + one Dupont jumper

Same idea as a jumper block: common = ISET; move **one** jumper to pick the current.

KiCad: `Conn_01x03` + `PinHeader_1x03_P2.54mm_Vertical`  
LCSC: search `2.54mm 1x3P` male pin header.

Do **not** change ILIM/VSET (13 kΩ) — that is not ICHG.

---

## B. Rails after SYS_5V

| # | Block | Candidate parts | Pick criteria | Circuit |
|---|-------|-----------------|---------------|---------|
| B1 | **5 V → 3.3 V** | AP2112K-3.3, or buck ≥500 mA | From **`SYS_5V`**, not from `V+` | `03` |
| B2 | Bulk / ceramics on 3V3 | 10 µF + 100 nF near ESP32 | Espressif guidelines | `03`/`05` |
| B3 | **TPS2662** P1 eFuse | **TPS2662x** | [slvaf94](https://www.ti.com/lit/pdf/slvaf94) ILIM ≈ 250–300 mA | `04` |
| B4 | TPS2662 support | RILIM, soft-start C, FLT, ceramics | Per datasheet | `04` |
| B5 | P1 bulk near RJ12 | 47–100 µF + 100 nF | Ghost inrush | `04`/`06` |
| B6 | **Selectable P1 ILIM** ○ | Jumper + RILIM set | Lab only — see below | `04` |

### B6 — Selectable P1 current limit (TPS2662 RILIM) — optional

Formula: **IOL ≈ 6.636 / RILIM** with RILIM in **kΩ**, IOL in **A**.  
DSMR continuous target ≈ **250 mA** → RILIM ≈ **26.5 kΩ** (use **26.7 kΩ** 1%).

| Target IOL | RILIM (calc) | Use (E96 1%) |
|------------|--------------|--------------|
| 100 mA | 66.4 kΩ | **66.5 kΩ** |
| 150 mA | 44.2 kΩ | **44.2 kΩ** |
| 250 mA | 26.5 kΩ | **26.7 kΩ** (default / production) |
| 300 mA | 22.1 kΩ | **22.1 kΩ** |

Same exclusive-jumper pattern as ISET: common = `ILIM` pin, one jumper only.  
Production boards can stuff only **26.7 kΩ** and omit the header.

---

## C. MCU + USB + storage

| # | Block | Candidate parts | Notes | Circuit |
|---|-------|-----------------|-------|---------|
| C1 | MCU | **ESP32-C3-MINI-1-N4** or **N4U** | Module | `05` |
| C2 | EN reset | 10 kΩ + 1 µF | | `05` |
| C3 | Decoupling | 100 nF + bulk | | `05` |
| C4 | Flash USB-C | Receptacle + **2× 5.1 kΩ** CC | May be 2nd connector | `01` |
| C5 | USB ESD | **USBLC6-2SC6** | D+/D− | `01`/`09` |
| C6 | **microSD** | Push-push holder, SPI | | `12` |

**Not needed:** external SDRAM / PSRAM.

---

## D. RJ12 P1 interface

| # | Block | Candidate parts | Notes | Circuit |
|---|-------|-----------------|-------|---------|
| D1 | RJ12 jack | 6P6C **female** | Meter side | `06` |
| D2 | Request opto | TLP2361 / 6N137 / Si86xx | Not PC817 @ 115200 | `07`/`11` |
| D3 | Data opto / OC | Fast opto ± FET | | `08`/`11` |
| D4 | Local Data pull-up | 4.7 kΩ → `P1_5V` | Bench | `08` |
| D5 | RJ12 ESD | Low-cap TVS on 1, 2, 5 | | `09` |

---

## E. Isolation

| # | Item | When | Circuit |
|---|------|------|---------|
| E1 | Signal optos | **In scope** | `11` |
| E2 | Isolated 5 V DC-DC | True floating RJ12 GND | `11` ○ |

---

## F. UI / debug

| # | Item | Notes | Circuit |
|---|------|-------|---------|
| F1 | Status LED | REQ / TX / error | `10` |
| F2 | Button | Profile select | `10` |
| F3 | OLED | Optional | `10` ○ |
| F4 | Test points | `V+`, `SYS_5V`, `P1_5V`, `VCC_3V3`, `P1_REQ`, `P1_DATA` | — |
| F5 | **2×5 pin header** | Debug / jumpers / ribbon — see below | `10` |

### F5 — 2×5 male pin header (PEC05DAAN class)

Classic black “Dupont” style: **10-position (2×5)**, **2.54 mm (0.100")** pitch, dual-row, **vertical through-hole male** pin header. Used on the Smart Meter Simulator for ribbon cable or jumper access (GPIO / rails / bring-up).

You do **not** need the Sullins **PEC05DAAN** brand part (Western premium pricing). Any standard Asian LCSC equivalent that matches the same footprint is fine (usually a few cents).

**Search on LCSC:** `2x5P 2.54mm` or `Pin Header 10 Position 2.54mm Dual Row`  
Filter for **Pin Headers** (open male pins), **straight / vertical**, through-hole — not right-angle, not female sockets, not shrouded IDC box headers unless you specifically want IDC.

Brands that usually stock drop-ins: **BOOMELE**, **XFCN**, **Wcon** (e.g. BOOMELE `2.54-2*5P` in the pin-header category). Confirm photo = open Dupont pins before ordering (many LCSC SKUs share the same MPN string).

**KiCad (built-in — no custom lib):**

| | Library entry |
|--|----------------|
| Symbol | `Connector_Generic:Conn_02x05_Odd_Even` |
| Footprint | `Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical` |

That places the exact 2×5 TH grid for a standard ribbon or Dupont jumpers.

---

## G. Explicitly skip

| Item | Why |
|------|-----|
| Omitting **TPS61023** | `V+` is not 5 V; Ghost fails on battery |
| Feeding P1 from `V+` / VSYS | Undervoltage vs DSMR |
| 3.3 V LDO from `V+` only | Browns out when cell ≈ 3.2 V |
| LoRa | Not needed |
| Stacked LiPo rider as primary | Superseded by integrated bq25185 + TPS61023 |
| External SDRAM | Wrong tool |
| Wi‑Fi as primary telegram store | Use microSD |

---

## H. KiCad net names

```
VBUS / VIN     charge USB (and optional DC)
VBAT           LiPo
V+ / VSYS      bq25185 pin 1 (3.0–4.5 V) — not P1 5V
SYS_5V         TPS61023 +5 V
VCC_3V3        from 5→3.3
P1_5V          TPS2662 output
GND / GND_ISO
P1_REQ / P1_REQ_MCU / MCU_P1_TX / P1_DATA
USB_D+ / USB_D-
SD_*
```

---

## I. KiCad order

1. bq25185 + TPS61023 (`02`) — sheet 1 in Slimme_meter_Sim  
2. 5→3.3 (`03`)  
3. TPS2662 (`04`)  
4. USB-C data (`01`)  
5. ESP32 (`05`)  
6. microSD (`12`)  
7. RJ12 + optos (`06`/`11`/`07`/`08`)  
8. ESD + UI (`09`/`10`)  

---

## J. Rough buy / BOM starters

- [ ] bq25185 + TPS61023 + inductor/passives (see Slimme_meter_Sim sheet 1)  
- [ ] 1S LiPo + JST  
- [ ] ESP32-C3-MINI-1-N4(U)  
- [ ] TPS2662  
- [ ] 5→3.3 regulator ≥500 mA  
- [ ] USB-C ×1 or ×2 + USBLC6  
- [ ] RJ12 6P6C female  
- [ ] High-speed optos ×2  
- [ ] microSD holder + card  
- [ ] LED, button, optional OLED  
- [ ] 2×5 2.54 mm male pin header (LCSC pin-header equiv. of PEC05DAAN)  
- [ ] Optional: iso 5V DC-DC  

Detail: `circuits/*/NOTES.txt`
