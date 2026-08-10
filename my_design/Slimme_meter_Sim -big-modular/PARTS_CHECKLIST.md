# Parts — big modular hand-build

## Modules (buy assembled)

| Item | Notes |
|------|--------|
| **ESP32-S3-DevKitC-1-N32R16V** | DigiKey **1965-ESP32-S3-DEVKITC-1-N32R16V-ND** — WROOM-2; males usually pre-soldered |
| **Male 1×22 header ×2** (spare / if DevKit bare) | Würth **61302211121** or 3M **929647-01-22-EU** — TH, 2.54 mm, vertical |
| **Female 1×22 socket ×2** (on main PCB) | Samtec **SSW-122-01-T-S** or Würth **61302211821** — TH, 2.54 mm; place rows **25.4 mm** apart |
| **USB-C breakout** | VBUS + GND to charger input only (not DevKit charge path) |
| **microSD breakout** | SPI; 3.3 V from DevKit `3V3` |
| LiPo 3.7 V | ≥2000 mAh recommended for multi-hour Ghost + Wi‑Fi |
| Optional: TPS2662 tiny carrier | Only if you keep foldback but refuse QFN on main |

## On main PCB — must hand-solder

| Item | Role | Package preference |
|------|------|--------------------|
| Charger IC (bq25185-class or equiv.) | USB → LiPo / VSYS | Largest available that still fits design |
| Boost IC (TPS61023-class or equiv.) | VSYS → **5V_SYS** | Bigger / hand-friendly |
| **TPS2662** + **TPS2553** | Dual eFuse; select one to RJ12 | Tiny QFN + SOT-23-6 |
| Jumper / 0 Ω / SPDT | Selects which eFuse feeds RJ12 | 2.54 mm jumper clearest |
| Schottky or ideal diode | 5V_SYS → DevKit `5V` | SOD-123 / SMA fine |
| Switch or jumper | Disconnect 5V_SYS from DevKit while flashing | Slide SW or 2.54 mm jumper |
| **6N137** DIP-8 ×2 | Request + Data | DIP / socket |
| RJ12 6P6C female | Meter jack | Through-hole |
| ESD (e.g. USBLC6 / PESD) | RJ12 | Whatever you can solder |
| Headers | DevKit, SD breakout, USB breakout | 2.54 mm |

### eFuse — buy **both** (dual footprint)

| Part | Role |
|------|------|
| **TPS2662** (exact variant + footprint in KiCad) | Primary attempt — foldback |
| **TPS2553DBVR** (SOT-23-6) | Fallback — current limit ~250–300 mA |
| 2.54 mm jumper **or** 0 Ω 0805 ×2 (fit one) **or** SPDT | `SEL` — never parallel both outputs |

Optional reference while PCB evolves: Adafruit **#6106** (charger+boost only).

## Do not put on main PCB (this revision)

- USB-C receptacle footprint (use breakout)
- microSD card cage (use breakout)
- ESP32 module reflow (use DevKitC)

## Do not wire

- DevKit USB VBUS / DevKit `5V` → charger VIN (creates charge loop when boost runs)
- Hard tie `5V_SYS` to DevKit `5V` with no switch (fight when programming)

## Firmware / bring-up order

1. Switch **OPEN** → flash DevKit over its USB  
2. Switch **CLOSED** → run from battery / main USB-C  
3. Enable Wi‑Fi config; stop using DevKit USB day-to-day  
4. SD breakout: load telegrams at home; field = replay only
