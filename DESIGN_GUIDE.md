# Smart Meter Simulator — Architecture & Day-by-Day Design Guide

**Goal:** Build a portable **DSMR P1 meter-side** board that behaves like a Dutch/Belgian smart meter P1 port, so you can develop and test devices like **P1 Ghost** without a real meter.

**MCU:** ESP32-C3-MINI-1 (Wi‑Fi)  
**Connector:** RJ12 6P6C (female = meter side)  
**Use case:** Fetch or generate P1 telegrams over Wi‑Fi / USB, and replay them on the P1 Data line when an OSM requests them.

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
│  ┌──────────┐   ┌─────────────────┐   ┌──────────────┐   ┌───────────┐ │
│  │ USB-C    │──►│ Power path +    │──►│ 5V rail      │──►│ RJ12 P1   │ │
│  │ (5 V in) │   │ battery charger │   │ (system +    │   │ female    │ │
│  └──────────┘   │ + power mux     │   │  P1 supply)  │   │           │ │
│                 └────────┬────────┘   └──────┬───────┘   │ 1 +5V     │ │
│                          │                   │           │ 2 REQ     │ │
│                    ┌─────▼─────┐       ┌─────▼─────┐     │ 3 DGND    │ │
│                    │ LiPo cell │       │ 3.3 V buck│     │ 4 NC      │ │
│                    │ + protect │       │ / LDO     │     │ 5 DATA    │ │
│                    └───────────┘       └─────┬─────┘     │ 6 PGND    │ │
│                                              │           └─────▲─────┘ │
│                                        ┌─────▼─────┐           │       │
│                                        │ ESP32-C3  │           │       │
│                                        │ MINI-1    │           │       │
│                                        └─────┬─────┘           │       │
│              ┌──────────────┐    ┌───────────┼───────────┐     │       │
│              │ Status LED   │◄───┤ GPIO      │ UART TX   │     │       │
│              │ + button     │    └───────────┼───────────┘     │       │
│              └──────────────┘                │                 │       │
│                                   ┌──────────▼──────────┐      │       │
│                                   │ A) Data Request     │◄─────┘ pin2  │
│                                   │    sense (5V→3.3V)  │              │
│                                   └─────────────────────┘              │
│                                   ┌─────────────────────┐              │
│                                   │ B) Open-collector   │────────────►│ pin5
│                                   │    Data driver      │              │
│                                   └─────────────────────┘              │
│                                   ┌─────────────────────┐              │
│                                   │ C) P1 +5V current   │────────────►│ pin1
│                                   │    limit / foldback │              │
│                                   └─────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Block checklist

| # | Block | You mentioned? | Verdict |
|---|--------|----------------|---------|
| 1 | USB-C input (power + native USB serial) | Yes | **Required** |
| 2 | ESP32-C3-MINI-1 (+ EN reset, strapping, caps) | Yes | **Required** |
| 3 | Battery + charger (USB → LiPo) | Yes | **Nice for portable lab**; optional if desk-only |
| 4 | Power mux (USB vs battery → 5V system) | Implied | **Required if battery** |
| 5 | 5V → 3.3V for MCU | Yes | **Required** |
| 6 | RJ12 +5V out with current limit | Yes (you said ~1.25 A) | **Required — but use DSMR numbers (below)** |
| 7 | Data Request / Enable sense | Yes | **Required** |
| 8 | Open-collector Data TX | Yes | **Required** |
| 9 | ESD on USB and RJ12 | Missing | **Strongly recommended** |
| 10 | Status LED + user button | Missing | **Recommended** |
| 11 | Test points / debug header | Missing | **Recommended** |
| 12 | Full galvanic isolation (optocouplers) | Missing | **Optional for a lab simulator** (real meters have it vs mains) |
| 13 | Firmware: telegram store / Wi‑Fi fetch / UART replay | Implied | **Required for the product to work** |

---

## 3. Important corrections (so architecture stays correct)

### 3.1 Current limit is **250 mA**, not 1.25 A

Per **DSMR P1 Companion Standard v5.0.2**:

| Spec | Value |
|------|--------|
| Continuous +5V to OSM | **≤ 250 mA** |
| Overload trip window | **~260–300 mA** |
| After short: foldback current | **≤ 50 mA** |
| Voltage at 250 mA | **≥ 4.9 V** (≤ 5.5 V idle) |
| Ripple at 250 mA | **≤ 100 mVpp** |

So the P1 power block should be a **5 V source + current limit / foldback around 250–300 mA**, not a 1.25 A supply.  
1.25 A would overpower OSM faults and is **not** what real meters do.

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

### 5.3 P1 +5V with current limit — essential

Pick one approach (simplest first):

| Approach | Pros | Cons |
|----------|------|------|
| **A. eFuse / current-limit IC** (e.g. TPS2592x, AP2280x class, or similar 5 V load switch with Ilim) | Clean foldback, auto-retry | Need correct Ilim set resistors |
| **B. Polyfuse ~0.3–0.5 A + series resistor** | Cheap | Soft, not exact DSMR foldback |
| **C. Dedicated LDO/buck + sense resistor + comparator shutoff** | Educational | More parts |

Target: **~250 mA continuous**, trip near **260–300 mA**, recover after fault.

Add bulk capacitance near RJ12 pin 1 (e.g. 100 µF low-ESR) so OSM Wi‑Fi bursts / inrush do not brown out.

### 5.4 USB-C + ESP32-C3

Reuse patterns from your P1 Ghost design:

- USB-C CC resistors (5.1 kΩ on CC1/CC2) for 5 V sink
- ESD (e.g. USBLC6-2SC6) on D+/D−
- ESP32-C3 native USB: **GPIO18 = D−, GPIO19 = D+**
- EN with RC reset; keep strapping pins clean (GPIO8/9 etc.)

### 5.5 Battery (optional but useful)

Typical path:

```
USB 5V ──► LiPo charger IC (e.g. TP4056 class or better: MCP73831 / BQ2407x)
              │
            LiPo + protection (DW01+FS8205 or protected cell)
              │
         Power mux / ideal diode ──► 5V boost OR system 5V rail
                                      │
                                 3.3V regulator ──► ESP32
```

If you only work at a desk: **skip battery v1**, power from USB only. Add battery in v2.

### 5.6 5V → 3.3V

- Buck (efficient, same family as Ghost SY8088) **or**
- LDO (simpler, hotter if ESP TX Wi‑Fi peak)

ESP32-C3 Wi‑Fi peaks matter: prefer a buck + good ceramics near the module.

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

1. **Correct P1 current limit (250 mA + foldback)** — not 1.25 A  
2. **Direction of each RJ12 pin** (you supply 5V; you sense Request; you OC-drive Data)  
3. **ESD** on RJ12 and USB  
4. **MCU support circuit** (EN, decoupling, USB ESD, antenna keep-out for Mini-1)  
5. **Power path clarity** (USB-only vs USB+battery mux)  
6. **Bulk caps** on P1 5V for OSM inrush / Wi‑Fi peaks  
7. **Status / debug** (LED, button, test points, UART or USB logs)  
8. **Firmware plan** (local telegram file vs Wi‑Fi download vs live generation + CRC16)  
9. **Isolation** only if you want meter-grade realism (optional for v1)  
10. **Mechanical:** RJ12 footprint orientation, battery holder / JST, USB-C mechanical strength

Your core idea is correct: USB + MCU + 5V + 3.3V + battery + Request sense + OC Data.  
The gaps are mostly **protection, current numbers, and bring-up aids**.

---

## 8. Day-by-day plan (~30 minutes each)

Work **one subcircuit per day**. End each day with: schematic snippet + part numbers + “how I will test it”.

### Week 1 — Power & MCU (desk version, no battery yet)

| Day | Subcircuit | Done when… |
|-----|------------|------------|
| **1** | System block diagram + net names | One-page diagram (section 2) locked; nets named: `USB_5V`, `SYS_5V`, `P1_5V`, `VCC_3V3`, `P1_REQ`, `P1_DATA`, `GND` |
| **2** | USB-C input | CC resistors, ESD, `USB_5V` net; can measure 5 V from a cable |
| **3** | 5V → 3.3V regulator | Module footprint + caps; 3.3 V stable under ~100 mA load |
| **4** | ESP32-C3-MINI-1 + EN + USB D+/D− | Board enumerates as USB serial / can flash a blink |
| **5** | Status LED + button | LED toggles from firmware; button readable |
| **6** | RJ12 connector footprint + GND pins | Pinout checked against DSMR table; silkscreen labeled 1…6 |
| **7** | Catch-up / ERC of power+MCU sheet | No floating power nets; ESD present |

### Week 2 — P1 electrical interface (the heart)

| Day | Subcircuit | Done when… |
|-----|------------|------------|
| **8** | P1_5V current-limit / load switch | Set for ~250 mA; short pin1–6 → current collapses / recovers |
| **9** | Bulk + ceramic decoupling on P1_5V | Scope voltage under pulsed load stays ≥ 4.9 V idea |
| **10** | Data Request sense divider / shifter | Apply 5 V on pin2 → MCU GPIO high; open → low |
| **11** | Open-collector Data driver | Scope pin5: idle high with pull-up; MCU TX toggles → clean edges |
| **12** | Wire Request→firmware gate TX | Only send UART when Request high |
| **13** | Replay a fixed DSMR telegram | P1 Ghost (or USB-serial adapter with pull-up) receives a valid frame |
| **14** | ESD on RJ12 (TVS array) + test points | TPs on `P1_5V`, `P1_REQ`, `P1_DATA`, `VCC_3V3` |

### Week 3 — Battery (optional) + polish

| Day | Subcircuit | Done when… |
|-----|------------|------------|
| **15** | Charger IC + charge LED | USB charges cell; terminates correctly |
| **16** | Battery protection / connector | Protected pack or DW01 circuit; correct polarity silk |
| **17** | Power mux USB vs battery | Hot-plug USB without brownout; battery powers when USB removed |
| **18** | Boost to 5V (if battery < 5V path needs it) | `SYS_5V` holds under P1 250 mA load |
| **19** | Mechanical: enclosure holes, antenna keep-out | Mini-1 RF keep-out clear of copper |
| **20** | Full ERC/DRC + BOM | Orderable BOM; all critical nets named |
| **21** | Bring-up checklist (print & keep) | See section 10 |

### Week 4 — Firmware product behaviour

| Day | Task |
|-----|------|
| **22** | USB CDC console: start/stop, show Request state |
| **23** | Store 1–N telegrams in flash / LittleFS |
| **24** | Wi‑Fi STA: download telegram JSON/text from your server |
| **25** | CRC16 check/fix for DSMR telegram footer |
| **26** | Auto-send every 1 s while Request high (DSMR-like) |
| **27** | Pair test with P1 Ghost end-to-end |
| **28** | Document known limits (no mains isolation, max 250 mA, etc.) |

If you only have **~30 min/day**, finishing Week 2 already gives a usable USB-powered simulator.

---

## 9. Recommended v1 vs v2

### v1 (ship first — simplest useful board)

- USB-C power + programming  
- ESP32-C3-MINI-1  
- 3.3 V regulator  
- RJ12 with current-limited 5 V  
- Request sense  
- Open-collector Data  
- LED + button  
- ESD  

**Skip:** battery, optocouplers, fancy foldback IC (use good load-switch with Ilim).

### v2

- LiPo + charger + mux  
- Closer DSMR foldback behaviour  
- Optional opto isolation on Request + Data  
- Better mechanical enclosure / pogo debug  

---

## 10. Bring-up checklist (print this)

1. USB plugged → `USB_5V` ≈ 5.0 V, `VCC_3V3` ≈ 3.3 V  
2. Flash blink firmware via USB  
3. No OSM connected: `P1_5V` ≈ 5 V, current ≈ 0  
4. Short `P1_5V` to GND briefly → protection trips / recovers (do not hold forever on crude polyfuse designs)  
5. Force `P1_REQ` to 5 V → MCU sees enable  
6. 4.7 kΩ pull-up pin5→5V, scope Data while sending “UUUU” → square-ish inverted UART  
7. Connect P1 Ghost → Ghost gets 5 V, asserts Request, receives telegram  
8. Wi‑Fi fetch path works (after firmware day)

---

## 11. Suggested part shortlist (starting point)

| Function | Example parts (verify footprints/stock) |
|----------|------------------------------------------|
| MCU | ESP32-C3-MINI-1-N4 or N4U |
| USB ESD | USBLC6-2SC6 |
| 3.3 V buck | SY8088 / AP3429 / similar 3.3 V |
| P1 current limit | 5 V eFuse/load switch, Ilim ≈ 0.25–0.3 A |
| OC driver | BSS138 or 2N7002 |
| RJ12 | 6P6C PCB jack (same family as Ghost) |
| TVS RJ12 | Low-cap ESD array on pins 1,2,5 |
| LED | Single LED + resistor (keep simple for v1) |
| Charger (v2) | MCP73831 or TP4056 module-equivalent discrete |
| Battery connector | JST-PH 2-pin |

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
