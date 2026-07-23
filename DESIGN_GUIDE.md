# Smart Meter Simulator — Architecture & Day-by-Day Design Guide

**Goal:** Build a portable **DSMR P1 meter-side** board that behaves like a Dutch/Belgian smart meter P1 port, so you can develop and test devices like **P1 Ghost** without a real meter.

**MCU:** ESP32-C3-MINI-1 (Wi‑Fi)  
**Power:** Seeed **Lipo Rider Plus** daughterboard (USB-C charge + 5 V + 3.3 V + LiPo)  
**Connector:** RJ12 6P6C (female = meter side)  
**Use case:** Fetch or generate P1 telegrams over Wi‑Fi / USB, and replay them on the P1 Data line when an OSM requests them.  
**Mechanical:** `mechanicals/lipo_rider_plus/` (reference footprint; you may draw your own)

---

## 1. What this board is (and is not)

| Role | Device | RJ12 side |
|------|--------|-----------|
| **This project (Simulator)** | Acts as the **meter** | Female jack, **supplies** +5V, **senses** Data Request, **drives** Data (open-collector) |
| P1 Ghost / OSM | Acts as the **reader** | Male plug, **takes** +5V, **drives** Data Request high, **reads** Data |

You already designed the reader side (P1 Ghost). This board is the **mirror image**.

```
Internet / USB ──► ESP32-C3 ──► open-collector UART ──► RJ12 pin5 (Data)
                      ▲                                      │
                      │                                      ▼
                 Enable sense ◄── RJ12 pin2 (Data Request) ◄── OSM (e.g. P1 Ghost)
                      │
                 +5V out ──────► RJ12 pin1 ──────────────────► powers OSM
```

---

## 2. Architecture overview (recommended blocks)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SMART METER SIMULATOR PCB                        │
│                                                                         │
│  ┌─────────────────────────────┐                        ┌───────────┐ │
│  │ Seeed Lipo Rider Plus       │──── 5V ───────────────►│ RJ12 P1   │ │
│  │ (daughterboard)             │                        │ female    │ │
│  │  USB-C charge → LiPo        │                        │ 1 +5V     │ │
│  │  out: 5V + 3V3              │─3V3──────────────┐     │ 2 REQ     │ │
│  └─────────────────────────────┘                  │     │ 3 DGND    │ │
│                                                   ▼     │ 4 NC      │ │
│  ┌──────────┐                              ┌──────────┐ │ 5 DATA    │ │
│  │ USB-C    │── D+/D− ────────────────────►│ ESP32-C3 │ │ 6 PGND    │ │
│  │ (flash)  │                              │ MINI-1   │ └─────▲─────┘ │
│  └──────────┘                              └────┬─────┘       │       │
│       Status LED / button ◄── GPIO              │             │       │
│                                   ┌─────────────┼───────┐     │       │
│                                   │ Request sense│ OC TX │─────┘       │
│                                   └─────────────┴───────┘             │
└─────────────────────────────────────────────────────────────────────────┘
```

P1 current-limit IC: **dropped**. Discrete charger design: **not needed** (Lipo Rider).

### Block checklist

| # | Block | You mentioned? | Verdict |
|---|--------|----------------|---------|
| 1 | USB-C input (power + native USB serial) | Yes | **Required** |
| 2 | ESP32-C3-MINI-1 (+ EN reset, strapping, caps) | Yes | **Required** |
| 3 | Lipo Rider Plus (USB-C charge + 5V + 3V3 + LiPo) | Yes | **Buy module** — see `mechanicals/lipo_rider_plus/` |
| 4 | On-board 5V↔battery mux / discrete charger | — | **Not needed** (inside Lipo Rider) |
| 5 | Extra 5V→3.3V regulator | — | **Removed** — use Lipo Rider 3V3 |
| 6 | RJ12 +5V out (direct from Lipo Rider) | Yes | **Required** — **no** current-limit IC |
| 7 | Data Request / Enable sense | Yes | **Required** |
| 8 | Open-collector Data TX | Yes | **Required** |
| 9 | ESD on USB and RJ12 | Missing | **Strongly recommended** |
| 10 | Status LED + user button | Missing | **Recommended** |
| 11 | Test points / debug header | Missing | **Recommended** |
| 12 | Full galvanic isolation (optocouplers) | Missing | **Optional for a lab simulator** (real meters have it vs mains) |
| 13 | Firmware: telegram store / Wi‑Fi fetch / UART replay | Implied | **Required for the product to work** |

---

## 3. Important corrections (so architecture stays correct)

### 3.1 P1 +5V current (lab choice)

DSMR meters guarantee ~250 mA continuous. **This simulator skips a
hardware current-limit IC** — Lipo Rider 5V goes straight to RJ12 pin 1.
Keep Ghost radios mutually exclusive (Wi‑Fi **or** LoRa) so average draw
stays reasonable. Optional bulk cap near pin 1 for inrush only.

### 3.2 Data Request polarity

- OSM sets pin 2 **HIGH (~5 V)** → meter **starts sending**
- OSM must **release** pin 2 to high‑Z to stop (must **not** drive it hard to GND)
- Your MCU only **senses** this line; it never drives RJ12 pin 2

### 3.3 Data line = open-collector + inverted UART

- Meter drives pin 5 as **open-collector / open-drain**
- Idle = pulled high by OSM (typically 1–10 kΩ to 5 V or 3.3 V)
- Logical UART bits are **inverted** relative to normal TTL UART (or you invert in HW/SW)
- Sink capability on meter side: up to **30 mA**; OSM should not pull more than **~5 mA**

### 3.4 Isolation

Real meters isolate P1 from mains with **optocouplers**.  
For a **USB/battery lab simulator**, full isolation is optional. Recommended minimum:

- Common GND between USB, battery, MCU, RJ12
- ESD diodes on RJ12 and USB
- Current-limited +5V out

Add optocouplers later only if you need max realism or extra USB-host protection.

---

## 4. RJ12 pin map (meter / simulator side)

| Pin | Name | Simulator must… |
|-----|------|------------------|
| 1 | +5V | **Source** 5 V, current-limited (~250 mA) |
| 2 | Data Request | **Sense** HIGH → enable TX (GPIO input) |
| 3 | Data GND | Tie to system GND |
| 4 | NC | Leave open |
| 5 | Data | **Open-collector** UART output from MCU TX |
| 6 | Power GND | Tie to system GND (same as pin 3) |

Serial (DSMR ≥ 4 / 5): **115200 8N1**, inverted open-drain on Data.

Official reference: [P1 Companion Standard (Netbeheer Nederland)](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf)

---

## 5. Typical reference circuits (copy these patterns)

### 5.1 Open-collector Data driver (pin 5) — essential

Same idea as [DSMRSim hardware](https://github.com/SanderBorra/DSMRSim):

```
ESP32 UART TX (3.3 V) ──► Gate of N-MOSFET (BSS138 / 2N7002)
Source ──────────────────► GND
Drain  ──────────────────► RJ12 pin 5 (Data)

Optional local pull-up 4.7 kΩ Drain → +5V
(OSM usually already has a pull-up; local one helps bench testing without OSM)
```

Behaviour:

- MCU TX idle HIGH → MOSFET off → Data floats / pulled HIGH (idle)
- MCU TX LOW → MOSFET on → Data pulled LOW (bit)

If firmware sends **non-inverted** UART, this MOSFET stage also **inverts** for free.  
If you use ESP UART `inverted` TX, wire accordingly (do not double-invert).

**Parts:** BSS138 or 2N7002, 100 Ω optional series gate, 4.7 kΩ pull-up, ESD diode to GND/5V.

### 5.2 Data Request sense (pin 2) — essential

```
RJ12 pin 2 (0…5 V) ──► divider (e.g. 10k / 10k) ──► ESP32 GPIO (~0…2.5 V)
                     └─► optional Schottky clamp / ESD
```

Or a single N-MOS / BJT level translator if you prefer a clean digital edge.

Firmware: when pin reads HIGH → start streaming telegrams; when released → stop UART TX.

**Do not** connect MCU GPIO directly to 5 V.

### 5.3 P1 +5V — direct (no limiter)

```
Lipo Rider 5V ──► SYS_5V / P1_5V ──► RJ12 pin 1
(+ optional 47–100 µF near the jack)
```

Circuit 04 is **dropped**. Do not add eFuse / polyfuse for v1.

### 5.4 USB-C data + ESP32-C3 (main board)

This is **flash/serial only** — not the battery charger.

- USB-C CC resistors (5.1 kΩ on CC1/CC2)
- ESD (e.g. USBLC6-2SC6) on D+/D−
- ESP32-C3 native USB: **GPIO18 = D−, GPIO19 = D+**
- EN with RC reset; keep strapping pins clean

### 5.5 Power = Seeed Lipo Rider Plus (buy)

Do not design charger / boost / mux on the main PCB.

- Wiki: https://wiki.seeedstudio.com/Lipo-Rider-Plus/
- Mount footprint: `mechanicals/lipo_rider_plus/Seeed_Lipo_Rider_Plus.kicad_mod`
- Wire header **5V** → `SYS_5V`, **3V3** → ESP32, **GND** → GND
- Plug 1S LiPo into module JST; charge via module USB-C
- Module has **no** D+/D− path to the ESP32

### 5.6 3.3 V for ESP32

Use Lipo Rider header **3V3** → `VCC_3V3`. No separate regulator on this board.
Put decoupling ceramics next to the ESP32 module.

---

## 6. Suggested ESP32-C3 pin assignment

| GPIO | Function | Notes |
|------|----------|--------|
| 18 / 19 | USB D− / D+ | Fixed by chip |
| U0TXD / chosen TX | P1 Data driver gate | Prefer a free UART TX |
| Free GPIO in | Data Request sense | After divider; not a strap pin |
| Free GPIO out | Status LED (or WS2812) | Optional |
| Free GPIO in | User button | Optional; avoid boot straps |
| EN | Reset | RC network |

Avoid putting ADC / Request sense on **strapping** pins used at boot.

---

## 7. What was missing from your mental model

1. **No P1 current-limit IC** (dropped on purpose)  
2. **Direction of each RJ12 pin** (you supply 5V; you sense Request; you OC-drive Data)  
3. **ESD** on RJ12 and USB  
4. **MCU support circuit** (EN, decoupling, USB ESD, antenna keep-out for Mini-1)  
5. **Bulk caps** on P1 5V for Ghost inrush (optional but cheap)  
6. **Status / debug** (LED, button, test points)  
7. **Firmware plan** (telegram store / Wi‑Fi fetch + CRC16)  
8. **Isolation** optional (v1 skip)  
9. **Mechanical:** Lipo Rider footprint (done in `mechanicals/`), RJ12 orientation

Power is settled: **Lipo Rider Plus** for 5V + 3.3V + charge; board USB-C for ESP32 data; RJ12 pin1 = direct 5V.

---

## 8. Day-by-day plan (~30 minutes each)

Work **one subcircuit per day**. End each day with: schematic snippet + part numbers + “how I will test it”.

### Week 1 — Power module + MCU

| Day | Subcircuit | Done when… |
|-----|------------|------------|
| **1** | Net names + Lipo Rider keep-out | Place `Seeed_Lipo_Rider_Plus` footprint; nets: `SYS_5V`, `P1_5V`, `VCC_3V3`, `P1_REQ`, `P1_DATA`, `GND` |
| **2** | Board USB-C (data) | CC + ESD; D+/D− to GPIO18/19 |
| **3** | Wire Lipo Rider 5V/3V3/GND | Module powered → rails OK |
| **4** | ESP32-C3-MINI-1 + EN | Flash blink over board USB-C |
| **5** | Status LED + button | LED toggles; button readable |
| **6** | RJ12 footprint | Pins 1…6 silk correct |
| **7** | ERC power+MCU | No floating rails; ESD present |

### Week 2 — P1 electrical interface (the heart)

| Day | Subcircuit | Done when… |
|-----|------------|------------|
| **8** | Route SYS_5V → RJ12 pin1 (+ optional bulk cap) | Ghost gets 5 V from P1; no limiter IC |
| **9** | (optional) Ceramic near P1_5V | Quiet rail under load |
| **10** | Data Request sense divider / shifter | Apply 5 V on pin2 → MCU GPIO high; open → low |
| **11** | Open-collector Data driver | Scope pin5: idle high with pull-up; MCU TX toggles → clean edges |
| **12** | Wire Request→firmware gate TX | Only send UART when Request high |
| **13** | Replay a fixed DSMR telegram | P1 Ghost (or USB-serial adapter with pull-up) receives a valid frame |
| **14** | ESD on RJ12 (TVS array) + test points | TPs on `P1_5V`, `P1_REQ`, `P1_DATA`, `VCC_3V3` |

### Week 3 — Polish (power already bought)

| Day | Subcircuit | Done when… |
|-----|------------|------------|
| **15** | Lipo Rider standoffs / header stack | Module mounts solid; charge via its USB-C |
| **16** | LiPo pack + polarity check | Protected 1S cell; runs hours in a corner |
| **17** | (spare) | — |
| **18** | (spare) | — |
| **19** | Enclosure + antenna keep-out | Mini-1 RF clear; USB-C / RJ12 accessible |
| **20** | Full ERC/DRC + BOM | Includes Lipo Rider as purchased part |
| **21** | Bring-up checklist | See section 10 |

### Week 4 — Firmware product behaviour

| Day | Task |
|-----|------|
| **22** | USB CDC console: start/stop, show Request state |
| **23** | Store 1–N telegrams in flash / LittleFS |
| **24** | Wi‑Fi STA: download telegram JSON/text from your server |
| **25** | CRC16 check/fix for DSMR telegram footer |
| **26** | Auto-send every 1 s while Request high (DSMR-like) |
| **27** | Pair test with P1 Ghost end-to-end |
| **28** | Document known limits (no P1 current limit IC, no mains isolation, etc.) |

If you only have **~30 min/day**, finishing Week 2 already gives a usable USB-powered simulator.

---

## 9. Recommended v1 vs v2

### v1 (ship this)

- **Lipo Rider Plus** + LiPo (5V + 3V3 + charge)  
- Board USB-C for ESP32 flash (D+/D−)  
- ESP32-C3-MINI-1  
- RJ12 with **direct** 5 V from Lipo Rider (no current-limit IC)  
- Request sense + open-collector Data  
- LED + button + ESD  

### v2

- Optional P1 isolation  
- Enclosure using GrabCAD STEP (see mechanicals README)  

---

## 10. Bring-up checklist (print this)

1. Lipo Rider up → `SYS_5V` / `VCC_3V3` OK  
2. Flash blink firmware via board USB  
3. `P1_5V` ≈ 5 V on RJ12 pin 1  
4. Force `P1_REQ` to 5 V → MCU sees enable  
5. 4.7 kΩ pull-up pin5→5V, scope Data while sending “UUUU” → square-ish inverted UART  
6. Connect P1 Ghost → Ghost gets 5 V, asserts Request, receives telegram  
7. Wi‑Fi fetch path works (after firmware day)

---

## 11. Suggested part shortlist (starting point)

| Function | Example parts (verify footprints/stock) |
|----------|------------------------------------------|
| Power daughterboard | **Seeed Lipo Rider Plus** + 1S LiPo |
| MCU | ESP32-C3-MINI-1-N4 or N4U |
| Board USB ESD | USBLC6-2SC6 |
| OC driver | BSS138 or 2N7002 |
| RJ12 | 6P6C PCB jack (same family as Ghost) |
| TVS RJ12 | Low-cap ESD array on pins 1,2,5 |
| LED | Single LED + resistor |
| Lipo Rider footprint | `mechanicals/lipo_rider_plus/Seeed_Lipo_Rider_Plus.kicad_mod` |

Reuse footprints/symbols from your existing EasyEDA→KiCad Ghost library where possible.

---

## 12. Relation to P1 Ghost

| Signal | Ghost (reader) | This simulator (meter) |
|--------|----------------|-------------------------|
| Pin 1 +5V | Input (power from meter) | **Output** (power OSM) |
| Pin 2 Request | MCU drives HIGH to enable | **MCU senses** HIGH |
| Pin 5 Data | Level-shift into UART RX | **OC drive** from UART TX |
| Goal | Parse / forward telegrams | Generate / replay telegrams |

Designing both makes a closed lab loop: **Simulator ↔ Ghost** with no real meter.

---

## 13. How to use this document

1. Lock the **architecture** (sections 2–3) before drawing PCB.  
2. Each day: open **section 8**, design only that block in KiCad.  
3. When stuck on a circuit, copy the matching pattern from **section 5**.  
4. Do not add battery or optos until **v1 USB + P1 interface** talks to Ghost.

---

## References

1. [DSMR P1 Companion Standard 5.0.2 (PDF)](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf) — official electrical rules  
2. [SanderBorra/DSMRSim](https://github.com/SanderBorra/DSMRSim) — open-collector meter-side MOSFET example  
3. [lvzon/dsmr-p1-parser](https://github.com/lvzon/dsmr-p1-parser) — P1 pinout + protocol notes  
4. Your repo: `P1_ghost_V2` — reader-side reverse of this board  

---

*Created for daily ~30 min subcircuit work. Start Day 1 with net names + block diagram, then USB power.*
