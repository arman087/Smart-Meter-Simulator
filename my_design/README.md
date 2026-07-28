# my_design

Your working area for the Smart Meter Simulator PCB.

```
my_design/
  libraries/          ← reference designs you study (do not edit as your product)
    adafruit_bq25185_5v_boost/
  (later) schematics / KiCad project sheets you own
```

## libraries/

Put third-party open-source PCBs here. Open them in KiCad/Eagle, then **copy** only what you need into *your* schematic (symbols, footprints, net ideas).

| Folder | Source | Use for |
|--------|--------|---------|
| `adafruit_bq25185_5v_boost/` | [Adafruit #6106 GitHub](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) | Charge + 5 V boost → integrate as `SYS_5V` |

### How to use a library entry

1. Open the `.sch` / `.brd` (Eagle) or convert/import into KiCad.
2. Study power path: USB-C → bq25185 → battery → TPS61023 → 5 V.
3. Copy the useful bits into your main project — omit solar pads / terminal block if unused.
4. Keep this folder as **read-only reference**; don’t turn it into the product PCB.

### Adafruit files in this clone

- `Adafruit bq25185 with 5V Boost Breakout.sch`
- `Adafruit bq25185 with 5V Boost Breakout.brd`
- `license.txt` (Adafruit / OSHW — respect when redistributing)
- `README.md` (upstream)

Original product: https://www.adafruit.com/product/6106  
Learn guide: https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board
