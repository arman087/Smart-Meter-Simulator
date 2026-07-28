# Parts checklist — choose in KiCad / DigiKey / JLCPCB

Use this while picking footprints and filling the schematic.  
Architecture is locked in [DESIGN_GUIDE.md](DESIGN_GUIDE.md) and [README.md](README.md).

**Legend:** ✅ buy / pick now · 🔧 design on PCB · ○ optional · ✗ skip

---

## A. Buy-as-module (mount on / next to main PCB)

| # | Item | Example | Notes | Status |
|---|------|---------|-------|--------|
| A1 | LiPo charger + 5 V boost | **Seeed Lipo Rider Plus** SKU 106990290 | Use **5V + GND + EN** only. **Do not power ESP32 from Rider 3V3** (250 mA). | ✅ |
| A2 | 1S LiPo | 1000–3000 mAh, **protected**, JST-PH | Size for hours of Ghost + Wi‑Fi | ✅ |
| A3 | microSD card | 8–32 GB, FAT32 | Telegram library | ✅ |

Footprint / header: `mechanicals/lipo_rider_plus/` — draw matching pads/header on main PCB.

**Alt (if you prefer Adafruit):** #6106 bq25185 + 5 V boost → same idea (5 V only) + your 5→3.3.

---

## B. Power on main PCB

| # | Block | Candidate parts | Pick criteria | Circuit |
|---|-------|-----------------|---------------|---------|
| B1 | **5 V → 3.3 V** | AP2112K-3.3, AMS1117-3.3, or your proven module/circuit; buck e.g. TPS62840 if you want efficiency | **≥500 mA**, preferably **1 A**; Wi‑Fi peaks | `03` |
| B2 | Bulk / ceramics on 3V3 | 10 µF + 100 nF near ESP32 | Espressif guidelines | `03`/`05` |
| B3 | **TPS2662** P1 eFuse | **TPS2662x** (check exact suffix / package on DigiKey) | Copy TI [slvaf94](https://www.ti.com/lit/pdf/slvaf94) RILIM ≈ 250–300 mA foldback | `04` |
| B4 | TPS2662 support | RILIM, soft-start C, FLT pull-up, input/output ceramics | Per datasheet + slvaf94 | `04` |
| B5 | P1 bulk near RJ12 | 47–100 µF ceramic/low-ESR + 100 nF | Ghost inrush | `04`/`06` |

Nets: `SYS_5V` (from Rider) → `VCC_3V3` and → TPS2662 → `P1_5V`.

---

## C. MCU + USB + storage

| # | Block | Candidate parts | Notes | Circuit |
|---|-------|-----------------|-------|---------|
| C1 | MCU | **ESP32-C3-MINI-1-N4** or **N4U** | Module, not chip-down | `05` |
| C2 | EN reset | 10 kΩ + 1 µF (Espressif) | | `05` |
| C3 | Decoupling | 100 nF + bulk per rail pins | | `05` |
| C4 | Board USB-C | USB-C receptacle + **2× 5.1 kΩ** CC1/CC2 | Flash / serial only | `01` |
| C5 | USB ESD | **USBLC6-2SC6** (or equal) | D+/D− | `01`/`09` |
| C6 | **microSD** | Push-push or push-pull holder, SPI or SDMMC | SPI is simpler on C3 | `12` |
| C7 | SD series / pull-ups | 10 kΩ CMD/DAT pull-ups if needed; 33–47 Ω series optional | Per Espressif SD notes | `12` |

**Not needed:** external SDRAM / PSRAM.

---

## D. RJ12 P1 interface (the product)

| # | Block | Candidate parts | Notes | Circuit |
|---|-------|-----------------|-------|---------|
| D1 | RJ12 jack | 6P6C **female** PCB mount (same family as Ghost if possible) | Meter side | `06` |
| D2 | Request opto | **PC817 too slow** → prefer **TLP2361**, **6N137**, or Si86xx digital isolator | 5 V Request → 3.3 V GPIO | `07`/`11` |
| D3 | Data opto / OC | High-speed opto **or** opto + FET on P1 side for true OC | 115200 baud | `08`/`11` |
| D4 | Opto LED resistors | Size for CTR / speed | Document polarity | `11` |
| D5 | Local Data pull-up | 4.7 kΩ `P1_DATA` → `P1_5V` | Bench without OSM | `08` |
| D6 | RJ12 ESD | Low-cap TVS array on pins 1, 2, 5 | | `09` |

**Pin map (meter):** 1=+5V out · 2=Request in · 3=GND · 4=NC · 5=Data OC · 6=GND

---

## E. Isolation (chosen for this build)

| # | Item | Candidate | When | Circuit |
|---|------|-----------|------|---------|
| E1 | Signal isolation | Optos / digital isolators above | **Yes — in scope** | `11` |
| E2 | Isolated 5 V for P1 | Murata/RECOM **B0505S-1W**, MEE1S0505SC, etc. (≥300 mA better) | Needed for **true** floating RJ12 vs USB GND | `11` |
| E3 | `GND` vs `GND_ISO` pours | PCB slot / keep-out | Only if E2 fitted | `11` |

If you skip E2 for first PCB spin: shared ground + optos still give DSMR-like signal path, but **not** full galvanic isolation.

---

## F. UI / debug

| # | Item | Candidate | Notes | Circuit |
|---|------|-----------|-------|---------|
| F1 | Status LED | 0603 LED + 1–3.3 kΩ | REQ / TX / error | `10` |
| F2 | User button | 6×6 tactile | Profile select; avoid strap pins | `10` |
| F3 | OLED (handy) | 0.96" SSD1306 I²C | Profile name, Request, SD OK | `10` ○ |
| F4 | Test points | `SYS_5V`, `P1_5V`, `VCC_3V3`, `P1_REQ`, `P1_DATA` | | — |
| F5 | Programming | Board USB-C CDC | Wi‑Fi later for OTA / UI | `01` |

---

## G. Explicitly skip

| Item | Why |
|------|-----|
| LoRa | Does not help P1 or Ghost Wi‑Fi tests |
| Rider **3V3** pin as ESP32 supply | Only 250 mA |
| Adafruit #6092 (3.3 V buck only) | No real 5 V for RJ12 |
| Wi‑Fi telegram download as primary store | Use **microSD** instead |
| External SDRAM | Wrong tool; flash + SD enough |

---

## H. KiCad sheet / net name starter

```
SYS_5V      from Lipo Rider 5V header
VCC_3V3     from 5→3.3 regulator
P1_5V       TPS2662 output (or after iso DC-DC)
GND         USB / MCU domain
GND_ISO     RJ12 domain (only if isolated DC-DC)
P1_REQ      RJ12 pin2
P1_REQ_MCU  after opto → GPIO
MCU_P1_TX   ESP32 UART TX
P1_DATA     RJ12 pin5
USB_D+ / USB_D-   GPIO19 / GPIO18
SD_MOSI/MISO/SCK/CS  (or SDMMC pins)
```

---

## I. Suggested order of work in KiCad

1. Net names + Lipo Rider header footprint (`02`)  
2. 5→3.3 (`03`)  
3. TPS2662 (`04`)  
4. USB-C data (`01`)  
5. ESP32-C3-MINI-1 (`05`)  
6. microSD (`12`)  
7. RJ12 (`06`)  
8. Optos Request + Data (`11` / `07` / `08`)  
9. ESD (`09`)  
10. LED / button / OLED (`10`)  
11. ERC / DRC / BOM export for JLCPCB  

---

## J. Rough buy list (modules + critical ICs)

Copy into a cart when ready:

- [ ] Seeed Lipo Rider Plus  
- [ ] 1S protected LiPo + cable  
- [ ] ESP32-C3-MINI-1-N4(U)  
- [ ] TPS2662 (exact orderable PN)  
- [ ] 5→3.3 regulator (your preferred PN / module)  
- [ ] USB-C receptacle + USBLC6-2SC6  
- [ ] RJ12 6P6C female  
- [ ] High-speed optos ×2 (or digital isolator)  
- [ ] Optional: isolated 5V/5V DC-DC ≥300 mA  
- [ ] microSD holder + card  
- [ ] LED, button, optional SSD1306  
- [ ] Passives / TVS as schematic grows  

Detail per block: `circuits/*/NOTES.txt`
