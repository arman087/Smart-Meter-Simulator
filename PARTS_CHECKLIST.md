# Parts checklist — choose in KiCad / DigiKey / JLCPCB

Use this while picking footprints and filling the schematic.  
Architecture is locked in [DESIGN_GUIDE.md](DESIGN_GUIDE.md) and [README.md](README.md).

**Legend:** ✅ buy / pick now · 🔧 design on PCB · ○ optional · ✗ skip

---

## A. Power (integrate on main PCB)

| # | Item | Example | Notes | Status |
|---|------|---------|-------|--------|
| A1 | Charger IC | **bq25185** | From Adafruit #6106 — USB charge, power path, BUVLO | 🔧 |
| A2 | 5 V boost | **TPS61023** + 1 µH + FB (R3/R4) | Boosts `V+`/`VSYS` → `SYS_5V`. **Do not omit** | 🔧 |
| A3 | Charge USB-C | Same family as #6106 | CC 5.1 kΩ; optional share data with ESP32 | 🔧 |
| A4 | Battery connector | JST-PH or pads for 2-wire LiPo | bq25185 manages charge + UVLO | ✅ |
| A5 | 1S LiPo | 1000–3000 mAh | 2-wire OK | ✅ |
| A6 | microSD card | 8–32 GB, FAT32 | Telegram library | ✅ |

Reference schematic/PCB: `my_design/libraries/adafruit_bq25185_5v_boost/`  
Product: https://www.adafruit.com/product/6106

**Nets:** `VBUS` → bq25185 → `V+`/`VSYS` (3.0–4.5 V) → TPS61023 → `SYS_5V` (+5 V)

---

## B. Rails after SYS_5V

| # | Block | Candidate parts | Pick criteria | Circuit |
|---|-------|-----------------|---------------|---------|
| B1 | **5 V → 3.3 V** | AP2112K-3.3, or buck ≥500 mA | From **`SYS_5V`**, not from `V+` | `03` |
| B2 | Bulk / ceramics on 3V3 | 10 µF + 100 nF near ESP32 | Espressif guidelines | `03`/`05` |
| B3 | **TPS2662** P1 eFuse | **TPS2662x** | [slvaf94](https://www.ti.com/lit/pdf/slvaf94) ILIM ≈ 250–300 mA | `04` |
| B4 | TPS2662 support | RILIM, soft-start C, FLT, ceramics | Per datasheet | `04` |
| B5 | P1 bulk near RJ12 | 47–100 µF + 100 nF | Ghost inrush | `04`/`06` |

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

---

## G. Explicitly skip

| Item | Why |
|------|-----|
| Omitting **TPS61023** | `V+` is not 5 V; Ghost fails on battery |
| Feeding P1 from `V+` / VSYS | Undervoltage vs DSMR |
| 3.3 V LDO from `V+` only | Browns out when cell ≈ 3.2 V |
| LoRa | Not needed |
| Lipo Rider Plus as primary | Superseded by integrated #6106 |
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

1. bq25185 + TPS61023 (`02`) — copy #6106  
2. 5→3.3 (`03`)  
3. TPS2662 (`04`)  
4. USB-C data (`01`)  
5. ESP32 (`05`)  
6. microSD (`12`)  
7. RJ12 + optos (`06`/`11`/`07`/`08`)  
8. ESD + UI (`09`/`10`)  

---

## J. Rough buy / BOM starters

- [ ] bq25185 + TPS61023 + inductor/passives (from #6106 BOM)  
- [ ] 1S LiPo + JST  
- [ ] ESP32-C3-MINI-1-N4(U)  
- [ ] TPS2662  
- [ ] 5→3.3 regulator ≥500 mA  
- [ ] USB-C ×1 or ×2 + USBLC6  
- [ ] RJ12 6P6C female  
- [ ] High-speed optos ×2  
- [ ] microSD holder + card  
- [ ] LED, button, optional OLED  
- [ ] Optional: iso 5V DC-DC  

Detail: `circuits/*/NOTES.txt`
