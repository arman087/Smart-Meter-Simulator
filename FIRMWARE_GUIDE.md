# Firmware guide — Smart Meter Simulator

**Audience:** firmware / bring-up for ESP32-C3 on this PCB.  
**Hardware:** `my_design/Slimme_meter_Sim/` · Architecture: [DESIGN_GUIDE.md](DESIGN_GUIDE.md) · Story: [DESIGN_REPORT.md](DESIGN_REPORT.md)  
**Pin map status:** locked for next PCB rev (Aug 2026 design session) — confirm nets in KiCad match this file before coding.

P1 behaviour follows [DSMR P1 Companion Standard 5.0.2](https://www.netbeheernederland.nl/sites/default/files/2024-02/dsmr_5.0.2_p1_companion_standard.pdf): **115200 8N1**, Request-gated TX, **open-collector Data**.

**MCU:** ESP32-C3-MINI-1-H4X (stay on C3 — no S3 / dual MCU for this rev).

---

## 1. Role of this firmware

This board is the **meter**. [P1 Ghost](https://github.com/arman087/P1_ghost) is the **reader**.

| Event | Firmware must… |
|-------|----------------|
| Ghost drives RJ12 **pin 2** Request high | Detect Request → **start** sending telegrams on Data |
| Ghost releases Request | **Stop** TX |
| Sending bits on **pin 5** | Only **pull Data low** for 0; idle/1 = high‑Z (Ghost pull-up) |
| Idle | Do not drive pin 2; do not push 5 V onto pin 5 |

Telegrams: **microSD** (primary). Wi‑Fi / USB CDC = config / OTA / UI (no LCD).

---

## 2. Locked pin / net map (ESP32-C3-MINI-1)

### 2.1 Full GPIO table

| Function | Net label | GPIO | Direction | Notes |
|----------|-----------|------|-----------|--------|
| USB D− | `USB_D-` | **18** | USB | Native USB flash / CDC |
| USB D+ | `USB_D+` | **19** | USB | Same |
| P1 Data TX | `ESP32_TX` | **21** | OUT (UART0 TX) | → 220 Ω → 6N137S (U8) |
| P1 Request in | `ESP32_enable` | **5** | IN | From 6N137S (U9); **active LOW** |
| RGB DIN | `Smart_RGB_LED_DIN` | **10** | OUT | WS-class LED |
| Strap | — | **2** | — | **10 kΩ to VCC_3V3** — do not use for app I/O at boot |
| Strap | — | **8** | — | **10 kΩ to VCC_3V3** — leave alone |
| BOOT / MODE | — | **9** | IN | Button to GND; pull-up. Bootloader if held at reset; **MODE** after boot |
| Chip reset | — | **EN** | — | RC + **RST** button to GND (not a GPIO) |
| SD SCK | `SD_SCK` | **0** | OUT | SPI |
| SD MOSI | `SD_MOSI` | **1** | OUT | SPI |
| SD MISO | `SD_MISO` | **3** | IN | SPI |
| SD CS | `SD_CS` | **6** | OUT | SPI (moved off GPIO4 for ADC) |
| Battery ADC | `BAT_ADC` | **4** | Analog | Divider mid-point (ADC1 only on GPIO0–4) |
| eFuse fault | `ESP32_FLT_Efuse` | **20** | IN | From 6N137S (U10) VO; **active LOW** = fault |
| Spare | — | **7** | — | Free / test pad (optional `SD_CD` later) |

### 2.2 Suggested `#define` block

```c
// USB: GPIO18 / GPIO19 (native) — no defines needed for CDC

#define PIN_P1_TX          21   // ESP32_TX → opto U8
#define PIN_P1_REQUEST     5    // ESP32_enable — active LOW
#define PIN_RGB            10

#define PIN_BOOT_MODE      9    // BOOT at reset; MODE button in app
// EN = hardware RST only

#define PIN_SD_SCK         0
#define PIN_SD_MOSI        1
#define PIN_SD_MISO        3
#define PIN_SD_CS          6

#define PIN_BAT_ADC        4    // ADC1
#define PIN_EFUSE_FLT      20   // ESP32_FLT_Efuse — active LOW

#define PIN_SPARE          7
```

### 2.3 Explicitly not used (do not soft-control)

| Idea | Why not |
|------|---------|
| GPIO → main power / boost EN | Chicken-and-egg; use mechanical **BAT** switch |
| GPIO → eFuse SHDN / P1 5 V enable | Ghost needs P1 5 V always available to boot and Request |
| Soft eFuse enable | HW pull-up keeps eFuse on; chip protects itself |
| LCD / shared SPI / 2nd ESP32 | Dropped for this rev |
| SD card-detect GPIO | Optional; poll `SD.begin()` / mount instead |
| Mux of STAT1/STAT2 | LEDs on charger are enough for charge *state* |

USB CDC and UART0 are **independent** on C3: program over USB; P1 Data uses **UART0 TX (GPIO21)** only.

---

## 3. Buttons and strapping

| Button | Connection | Firmware |
|--------|------------|----------|
| **RST** | Momentary EN → GND (+ existing RC POR) | Hardware reset only |
| **BOOT / MODE** | Momentary GPIO9 → GND (+ pull-up to 3V3) | Hold + RST → download; after boot = user MODE |

Straps at reset (must be HIGH for normal boot):

- **GPIO2**, **GPIO8**: fixed 10 kΩ pull-ups — **no switches** on these pins  
- **GPIO9**: HIGH = normal boot; LOW = download  

Do **not** hang loads that pull GPIO2/8/9 low at power-up.

---

## 4. Optocouplers — polarity (critical)

Parts: **AOTE 6N137S** (LCSC C20612601). Open-collector `VO`. Shared board GND.

### 4.1 Data out — U8 (ESP32 → RJ12 pin 5)

```
GPIO21 ── 220 Ω ── LED ── GND
VCC/EN = SYS_5V + 100 nF
VO ──► RJ12 pin 5     ← no pull-up on this PCB (Ghost pulls up)
```

| ESP32 TX | LED | pin 5 |
|----------|-----|-------|
| LED on | On | **LOW** (0) |
| LED off | Off | Open → Ghost pull-up HIGH |

Firmware: UART0 **115200 8N1** on GPIO21; expect **TX invert** (opto inverts). **TX only while Request active.**

### 4.2 Request in — U9 (RJ12 pin 2 → ESP32)

```
RJ12 pin2 ── 330 Ω ── LED ── GND
VO ──► ESP32_enable ── 10 kΩ to VCC_3V3 ──► GPIO5
```

| Ghost Request | `ESP32_enable` / GPIO5 |
|---------------|-------------------------|
| Idle | **HIGH** |
| Active | **LOW** |

**Request active = GPIO5 LOW.** Start/stop telegram stream on that.

### 4.3 eFuse FLT — U10 (TPS26625 → ESP32)

Keep eFuse `FLT` on **5 V** domain (100 kΩ pull-up to `SYS_5V`). Do **not** wire FLT directly to a GPIO.

```
SYS_5V ── 330 Ω ── 6N137 anode (pin 2)
Efuse_FLT ────────── 6N137 cathode (pin 3)   ← same net as TPS26625 FLT
6N137 VCC/EN = SYS_5V + 100 nF
VO (pin 6) ──► ESP32_FLT_Efuse ── 10 kΩ to VCC_3V3 ──► GPIO20
```

| eFuse | LED | `ESP32_FLT_Efuse` / GPIO20 |
|-------|-----|----------------------------|
| OK | off | **HIGH** |
| Fault | on | **LOW** |

Firmware: fault = GPIO20 **LOW** → RGB warning / stop TX / log over USB.

---

## 5. microSD (Hirose DM3AT-SF-PEJM5)

Connector: **Card1** / DM3AT-SF-PEJM5. SPI only. Power **VCC_3V3** only.

| Card pin | Name | Net | ESP32 |
|----------|------|-----|-------|
| 1 | DAT2 | NC (or 10 kΩ to 3V3) | — |
| 2 | CD/DAT3 | `SD_CS` | GPIO6 |
| 3 | CMD | `SD_MOSI` | GPIO1 |
| 4 | VDD | `VCC_3V3` + 10 µF + 100 nF | — |
| 5 | CLK | `SD_SCK` | GPIO0 |
| 6 | VSS | GND | — |
| 7 | DAT0 | `SD_MISO` | GPIO3 |
| 8 | DAT1 | NC (or 10 kΩ to 3V3) | — |
| 9 | SW_B | GND or NC | — |
| 10–14 | shell / SW_A | GND; SW_A unused (no `SD_CD`) | — |

Optional 33–47 Ω series on SCK/MOSI/MISO/CS. Keep away from antenna keep-out.

Firmware:

```c
SPI.begin(PIN_SD_SCK, PIN_SD_MISO, PIN_SD_MOSI, PIN_SD_CS);
SD.begin(PIN_SD_CS);
// FatFS path e.g. /telegrams/*.txt
```

No card-detect GPIO: mount at boot / on demand; fail → RGB / USB message. Hot-plug not required for v1.

---

## 6. Battery voltage (`BAT_ADC`)

**Purpose:** approximate SoC / “charge me” on RGB. Not a fuel gauge.  
STAT1/STAT2 LEDs on bq25185 already show charge *state* — do not mux them into the MCU.

### 6.1 Circuit (place divider next to ESP32)

Sense **after** mechanical BAT power switch (no drain when BAT OFF):

```
Battery(+) ──[SW_BAT]── BAT_SENSE ──► bq25185 BAT
                              │
                              └── 100 kΩ (1%) ──●── BAT_ADC ──► GPIO4
                                                 │
                                                 ├── 100 kΩ (1%) ── GND
                                                 └── 100 nF ────── GND
```

Equal **100 kΩ / 100 kΩ** → \(V_{ADC} = V_{BAT}/2\) → 4.2 V → **2.1 V**.  
**1%** resistors are enough (ADC error dominates; 0.1% not needed).  
Cap is **in parallel with the bottom resistor**, at the ADC pin.

### 6.2 Firmware hints

- Use **ADC1** on GPIO4.  
- Low threshold example: Vbat ≲ 3.5 V → \(V_{ADC}\) ≲ 1.75 V → blink RGB “charge me”.  
- Calibrate once against a DMM if you want better %.

---

## 7. Mechanical power switches (not GPIOs)

| Switch | Net path | Part class |
|--------|----------|------------|
| **SW_BAT** | Cell + → switch → bq25185 **BAT** | Metal mini toggle e.g. ST-0-102 / Dailywell 3 A |
| **SW_USB** | USB-C VBUS → `5V_usb` → switch → `5V_usb_1` → bq25185 **IN** | Same |

Example USB wiring: COM/throw between `5V_usb` and `5V_usb_1`; frame/support pin → **GND**. Do not switch CC or USB D+/D−.

Do **not** use MSK12C02 (50 mA ISET switch) on these paths.

---

## 8. RJ12 meter-side map

| Pin | Net | Firmware |
|-----|-----|----------|
| 1 | `P1_5V` | After TPS26625 — no GPIO |
| 2 | `RJ12_pin2` | Request → U9 → GPIO5 |
| 3 | GND | — |
| 4 | NC | — |
| 5 | `RJ12_Tx_pin5` | Data ← U8 ← GPIO21 |
| 6 | GND | — |

---

## 9. Power / eFuse notes

| Rail | Use |
|------|-----|
| `SYS_5V` | Boost 5 V; SY8088, opto VCC, RGB path |
| `VCC_3V3` | ESP32, SD, logic pull-ups, `ESP32_FLT_Efuse` pull-up |
| `P1_5V` | TPS26625 out → RJ12 pin 1 (~250 mA) |

- TPS26625 **SHDN**: hardware enabled (e.g. 100 kΩ to 5 V) — **no MCU pin**.  
- FLT → opto → GPIO20 only (see §4.3).  
- SY8088AAC (~1 A) is enough for C3 + SD + Wi‑Fi for this design.

---

## 10. Suggested bring-up order

1. USB CDC hello (GPIO18/19).  
2. RST + BOOT (GPIO9) work; normal boot with GPIO9 released.  
3. RGB on GPIO10.  
4. GPIO5 Request: active LOW with Ghost or bench 5 V on pin 2.  
5. UART0 TX GPIO21 + invert; gate on Request.  
6. `ESP32_FLT_Efuse` GPIO20 (force fault / overload test).  
7. SD mount + list `/telegrams`.  
8. `BAT_ADC` vs DMM; low-batt RGB.  
9. MODE on GPIO9 (short/long) + Wi‑Fi config UI.

### Quick test without Ghost

- Request: drive RJ12 pin 2 into the opto LED path → GPIO5 LOW.  
- Data: optional bench **4.7 kΩ** pin 5 to `P1_5V`; remove for normal Ghost use.

---

## 11. Checklist for the firmware author

- [ ] Flash via USB (GPIO18/19); BOOT+RST for recovery.  
- [ ] P1 UART **GPIO21**, 115200 8N1, invert as needed.  
- [ ] Request **GPIO5**, active LOW; TX only while LOW.  
- [ ] SD SPI 0/1/3/6; FatFS telegrams.  
- [ ] FLT **GPIO20**, active LOW.  
- [ ] BAT ADC **GPIO4**; low-batt indication.  
- [ ] GPIO9 = MODE in app; never leave low at reset unintentionally.  
- [ ] Never drive GPIO2/8 against strap pull-ups at boot.  
- [ ] No 5 V into any ESP32 GPIO.  
- [ ] No software enable of P1 eFuse or main power.

---

## 12. Related circuit notes

| Topic | File |
|-------|------|
| Request sense | [circuits/07_data_request_sense/NOTES.txt](circuits/07_data_request_sense/NOTES.txt) |
| Data OC / opto | [circuits/08_open_collector_data/NOTES.txt](circuits/08_open_collector_data/NOTES.txt) |
| ESP32 | [circuits/05_esp32_c3_mini/NOTES.txt](circuits/05_esp32_c3_mini/NOTES.txt) |
| P1 eFuse | [circuits/04_p1_5v_current_limit/NOTES.txt](circuits/04_p1_5v_current_limit/NOTES.txt) |
| microSD | [circuits/12_microsd/NOTES.txt](circuits/12_microsd/NOTES.txt) |
| Parts | [PARTS_CHECKLIST.md](PARTS_CHECKLIST.md) |
