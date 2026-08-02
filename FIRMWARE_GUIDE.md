# Firmware guide — Smart Meter Simulator

**Audience:** firmware / bring-up for ESP32-C3 on this PCB.  
**Hardware:** `my_design/Slimme_meter_Sim/` · Architecture: [DESIGN_GUIDE.md](DESIGN_GUIDE.md) · Story: [DESIGN_REPORT.md](DESIGN_REPORT.md)

P1 behaviour follows [DSMR P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf): **115200 8N1**, Request-gated TX, **open-collector Data**.

---

## 1. Role of this firmware

This board is the **meter**. [P1 Ghost](https://github.com/arman087/P1_ghost) is the **reader**.

| Event | Firmware must… |
|-------|----------------|
| Ghost drives RJ12 **pin 2** Request high | Detect Request → **start** sending telegrams on Data |
| Ghost releases Request | **Stop** TX |
| Sending bits on **pin 5** | Only **pull Data low** for 0; idle/1 = high‑Z (Ghost pull-up) |
| Idle | Do not drive pin 2; do not push 5 V onto pin 5 |

Telegrams: later from **microSD** (primary). Wi‑Fi = config / OTA, not the main telegram pipe.

---

## 2. Pin / net map (ESP32-C3-MINI-1)

Confirm nets in KiCad before locking code. Names below match current schematic labels.

| Function | Net (schematic) | Module / chip pin | Notes |
|----------|-----------------|-------------------|--------|
| USB D− | `USB_D-` | **GPIO18** | Native USB flash / CDC |
| USB D+ | `USB_D+` | **GPIO19** | Same |
| **P1 Data TX** | `ESP32_TX` | **GPIO21 (`TXD0`)** | → 220 Ω → 6N137S (U8) LED |
| **P1 Request in** | `ESP32_enable` | **Assign free GPIO** | From 6N137S (U9) VO; see §3 |
| RGB DIN | `Smart_RGB_LED_DIN` | **GPIO10** | WS-class LED via 300 Ω |
| Strapping | — | **GPIO2**, **GPIO8** | 10 kΩ pull-ups on PCB — leave as inputs or don’t fight boot |
| EN | — | EN | External RC to 3V3 — not a GPIO |
| UART0 RX | — | GPIO20 (`RXD0`) | Free / unused for P1 |
| Switches (if stuffed) | `ESP32_Sw` | GPIO4 / GPIO5 | Optional UI |

**Request GPIO:** wire `ESP32_enable` to any free input (e.g. **GPIO0, GPIO1, GPIO6, GPIO7**). Avoid GPIO9 if you care about download-strap. Document the final number in this table when the schematic pin is locked.

USB CDC and UART0 are **independent** on ESP32-C3: program over USB; use **UART0 TX (GPIO21)** for P1 Data.

---

## 3. Optocouplers — polarity (critical)

Both channels: **AOTE 6N137S** (LCSC C20612601). Open-collector `VO`. Shared board GND (not galvanic isolation).

### 3.1 Data out — U8 (ESP32 → RJ12 pin 5)

```
GPIO21 ── 220 Ω ── LED ── GND
VCC/EN = SYS_5V (+5 V before eFuse) + 100 nF
VO ──► RJ12 pin 5     ← NO pull-up on this PCB (Ghost pulls up)
```

| ESP32 TX level | LED | VO / pin 5 |
|----------------|-----|------------|
| Drives LED **on** | On | **LOW** (0) |
| LED **off** | Off | **Open** → Ghost pull-up = HIGH (1) |

Firmware:

- Use **UART0** @ **115200 8N1** on GPIO21.
- Expect **logic invert** vs a normal UART wire — 6N137 inverts (LED on → VO low). Enable **TX invert** (or invert in software) so a UART “mark/space” matches DSMR after you scope it with Ghost.
- **Only TX while Request is active** (§3.2).
- Never configure this pin as push-pull into pin 5 without the opto.

LED current @ 3.3 V, Vf ≈ 1.33 V, **220 Ω** ≈ **9 mA** (OK for GPIO; threshold ~5 mA, max 20 mA).

### 3.2 Request in — U9 (RJ12 pin 2 → ESP32)

```
RJ12 pin2 ── 330 Ω ── LED ── GND
VCC/EN = SYS_5V + 100 nF
VO ──► ESP32_enable ── 10 kΩ pull-up to VCC_3V3 ──► GPIO input
```

**Pull-up must be 3.3 V, never 5 V** (ESP32 not 5 V tolerant).

| Ghost Request | LED | `ESP32_enable` |
|---------------|-----|----------------|
| Idle / released | Off | **HIGH** (3.3 V via 10 kΩ) |
| Active (~4.9–5 V on pin 2) | On | **LOW** |

Firmware:

- Configure GPIO as **input**, pull-up optional (board already has 10 kΩ).
- **Request active = GPIO LOW.**
- On falling edge (or poll LOW): start telegram stream.
- On rising edge / HIGH: stop TX promptly.
- Debounce lightly if needed; Request is mostly DC but can glitch on plug.

LED current @ ~4.9 V, Vf ≈ 1.33 V, **330 Ω** ≈ **11 mA**.

---

## 4. RJ12 meter-side map

| Pin | Net | Firmware relevance |
|-----|-----|--------------------|
| 1 | `RJ12_5V` / `P1_5V` | Power out via TPS26625 — no GPIO |
| 2 | `RJ12_pin2` | Request in → U9 → `ESP32_enable` |
| 3 | GND | — |
| 4 | NC | — |
| 5 | `RJ12_Tx_pin5` | Data OC out ← U8 ← `ESP32_TX` |
| 6 | GND | — |

---

## 5. Power / eFuse notes for firmware

| Rail | Use |
|------|-----|
| `SYS_5V` | Boost 5 V; feeds SY8088, opto VCC, RGB path (via Schottky) |
| `VCC_3V3` | ESP32, logic pull-ups |
| `P1_5V` | After **TPS26625** → RJ12 pin 1 only |

- **TPS26625** = hiccup / auto-retry — no need to toggle SHDN for overload recovery.
- SHDN is hard-tied enabled in hardware; optional later: GPIO kill switch (not required for v1).
- Opto `VCC` is on **SYS_5V** so P1 current limit (~250 mA) stays available for Ghost.
- Do not expect firmware to “send 5 V” on Data — only open-drain zeros.

---

## 6. Suggested bring-up order (firmware)

1. USB CDC: `hello` over native USB (GPIO18/19).  
2. Blink / RGB on GPIO10.  
3. Scope or LED on `ESP32_enable`: plug Ghost or apply 5 V on pin 2 → GPIO goes **LOW**.  
4. UART0 TX @ 115200 on GPIO21 into U8; with Ghost connected and Request high, send test pattern (`U` stream); adjust **invert** until Ghost parses.  
5. Gate TX on Request LOW only.  
6. microSD telegram files + Wi‑Fi config (when hardware present).

### Quick test without Ghost
- Request: temporarily pull RJ12 pin 2 to 5 V through the 330 Ω path (or jumper carefully) → `ESP32_enable` LOW.  
- Data: optional **4.7 kΩ** from pin 5 to `P1_5V` on the bench only; remove for normal Ghost use.

---

## 7. Checklist for the firmware author

- [ ] Flash via USB only (no UART0 jig required).  
- [ ] P1 UART on **GPIO21**, 115200 8N1, invert as needed.  
- [ ] Request GPIO = `ESP32_enable` net, **active LOW**.  
- [ ] TX runs **only** while Request is LOW.  
- [ ] No 5 V into any ESP32 GPIO.  
- [ ] Strapping pins GPIO2/8 not driven wrong at boot.  
- [ ] Document final Request GPIO number here when schematic pin is fixed.  
- [ ] Telegram source: microSD path TBD; Wi‑Fi secondary.

---

## 8. Related circuit notes

| Topic | File |
|-------|------|
| Request sense | [circuits/07_data_request_sense/NOTES.txt](circuits/07_data_request_sense/NOTES.txt) |
| Data OC / opto | [circuits/08_open_collector_data/NOTES.txt](circuits/08_open_collector_data/NOTES.txt) |
| ESP32 | [circuits/05_esp32_c3_mini/NOTES.txt](circuits/05_esp32_c3_mini/NOTES.txt) |
| P1 eFuse | [circuits/04_p1_5v_current_limit/NOTES.txt](circuits/04_p1_5v_current_limit/NOTES.txt) |
| Parts / RILIM | [PARTS_CHECKLIST.md](PARTS_CHECKLIST.md) |
