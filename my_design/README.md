# my_design

Your working area for the Smart Meter Simulator PCB.

```
my_design/
  libraries/          ← reference designs you study (do not edit as your product)
    adafruit_bq25185_5v_boost/
  (later) your KiCad project sheets
```

## libraries/

| Folder | Source | Use for |
|--------|--------|---------|
| `adafruit_bq25185_5v_boost/` | [Adafruit #6106 GitHub](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) | **Integrate both ICs** onto main PCB |

### Power path (locked)

```
USB-C → bq25185 → V+ / VSYS (3.0–4.5 V) → TPS61023 → +5V (SYS_5V)
```

- **bq25185** pin 1 = `VSYS` (Adafruit net `V+`) — **not** 5 V  
- **TPS61023** is **required** — do not delete the boost sheet when copying  

### How to use

1. Open KiCad project under `adafruit_bq25185_5v_boost/Adafruit bq25185 with 5V Boost Breakout/`  
   (or Eagle `.sch` / `.brd` at the folder root).  
2. Copy bq25185 **and** TPS61023 (plus inductor, FB, input path) into your product schematic.  
3. Omit solar pads / terminal block if unused.  
4. Then add circuits `03` (5→3.3), `04` (TPS2662), ESP32, SD, RJ12, optos.

### Upstream

- Product: https://www.adafruit.com/product/6106  
- Guide: https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board  
- `license.txt` — Adafruit OSHW; respect when redistributing  
