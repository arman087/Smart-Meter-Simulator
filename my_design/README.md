# my_design

Working KiCad for the Smart Meter Simulator:

```
my_design/
  Slimme_meter_Sim/          ← product project (start here)
    SCH_1_USB_5volt_sch…     USB-C → bq25185 → TPS61023 → SYS_5V
```

## Power nets

```
USB-C → bq25185 → V+ / VSYS (3.0–4.5 V) → TPS61023 → +5V (SYS_5V)
```

- **bq25185** system rail = `VSYS` (schematic `V+`) — **not** 5 V  
- **TPS61023** is **required** — do not feed P1 or the 3.3 V regulator from `V+` alone  

## Docs

- [DESIGN_REPORT.md](../DESIGN_REPORT.md) — why / how so far  
- [DESIGN_GUIDE.md](../DESIGN_GUIDE.md) — architecture checklist  
- [PARTS_CHECKLIST.md](../PARTS_CHECKLIST.md)  

## Silicon refs

- https://www.ti.com/product/BQ25185  
- https://www.ti.com/product/TPS61023  
- https://www.ti.com/lit/pdf/slvaf94 (P1 foldback / TPS2662)
