# Slimme meter Sim — big modular (hand-build)

**Active path:** this folder only.  
Parent `DESIGN_GUIDE.md` / root README are **not** source of truth for this build.

Portable **DSMR P1 meter-side** simulator: battery in a corner, Ghost on RJ12, Wi‑Fi range tests without a real meter.

---

## Locked modular plan (return-to-work)

| Piece | How it is built |
|-------|-----------------|
| **ESP32-S3** | **Module:** Espressif **ESP32-S3-DevKitC-1-N32R16V** (**WROOM-2**, 32 MB flash + 16 MB PSRAM) — same 2×22 headers, onboard 5 V→3.3 V LDO. Alt: **N16R8V** |
| **USB-C (charge)** | **Breakout module** → soldered/wired to main PCB (not a tiny USB-C footprint on your board) |
| **microSD** | **Breakout module** → SPI wires to DevKit (not onboard SD slot) |
| **Charger IC** | On **main PCB** — hand-solder (bigger package preferred) |
| **5 V boost** | On **main PCB** — hand-solder (**bigger package** preferred) |
| **eFuse / current limit** | On **main PCB** — **both** TPS2662 + TPS2553, select with jumper / 0 Ω |
| **Optos + RJ12** | On **main PCB** — **6N137 DIP-8** ×2, RJ12, ESD |

**Not on main PCB:** DevKit MCU, USB-C receptacle soldering challenge, SD cage soldering challenge.

---

## Power rules (do not loop-charge)

```
Main USB-C breakout ──► charger ──► LiPo / VSYS ──► boost ──► 5V_SYS
                                                              ├── eFuse → RJ12 pin 1
                                                              └── [SW] ──|>|──► DevKit "5V"

DevKit USB ──► program / first flash ONLY
               NEVER wired into the charger
```

| Rule | Why |
|------|-----|
| **Only main USB-C charges** | Avoids boost → DevKit 5V → charger fake-charge loop |
| **`[SW]` between 5V_SYS and DevKit `5V`** | Open while programming on DevKit USB; closed for normal run |
| **Diode on 5V_SYS → DevKit** | Extra reverse protection when switch is closed and habits slip |
| **After first flash** | Prefer Wi‑Fi / OTA; leave DevKit USB unused |

### Switch habit

| Mode | Switch `5V_SYS → DevKit` | USB |
|------|--------------------------|-----|
| First flash / recovery | **OPEN** | DevKit USB only |
| Field / normal | **CLOSED** | Main USB-C charge (or battery); talk over Wi‑Fi |

---

## Hand-solder focus (your three ICs)

1. **Charger** (e.g. path like bq25185-class / Adafruit #6106 as reference)  
2. **Boost** — bigger package / module-friendly footprint  
3. **eFuse** — see decision below  

Everything else painful (USB-C, SD) = **bought breakouts**.

---

## eFuse: populate **both**, select one

Put **TPS2662** (foldback / rich) **and** **TPS2553** (bigger / easy) on the same PCB. Only one path to RJ12 pin 1 is live.

```
5V_SYS ──┬──► TPS2662 ──┐
         │              ├── [jumper / 0 Ω / SW] ──► RJ12 pin1
         └──► TPS2553 ──┘
```

| Select | When |
|--------|------|
| **TPS2662 path** | Reflow succeeded — use the “amazing” part |
| **TPS2553 path** | Tiny IC bridged / dead / skipped — still ship the board |

**Select hardware (pick one style in KiCad):**
- Two **0 Ω** positions (fit only one), or  
- **2.54 mm jumper** ( clearest for bring-up), or  
- SPDT switch (handy, slightly more drop/noise — fine for P1)

**Do not** leave both outputs paralleled with no select — fight / odd current paths.

Try the tiny IC with paste + hot plate; if it fails, open that path and close TPS2553. No board respin required.

---

## Tomorrow checklist

1. KiCad: power sheet — charger → VSYS → boost → `5V_SYS`  
2. KiCad: DevKit header footprint + **SW + diode** to DevKit `5V`  
3. KiCad: USB-C **breakout** connector footprint / pin header (VBUS, GND, maybe CC if needed)  
4. KiCad: SD **breakout** header (SPI + 3V3 + GND)  
5. KiCad: **both** eFuse footprints + **select jumper/0 Ω** → RJ12  
6. KiCad: 6N137 ×2 + ESD  

Detail: [ARCHITECTURE.md](ARCHITECTURE.md) · [PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)
