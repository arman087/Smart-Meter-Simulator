# Slimme meter Sim — DevKit with real battery → 5 V

**Active path:** this folder.  
**Do not use SparkFun Thing Plus** for this product — it has **no 5 V boost** from the JST battery.

## What you actually need from the DevKit

| Must have | Why |
|-----------|-----|
| ESP32-S3 (or strong S3) | MCU + Wi‑Fi |
| USB-C | Flash + charge |
| microSD | Telegrams |
| LiPo / battery management | JST (or internal pack) |
| **Regulated ~5 V out while on battery** | Feed TPS2553 → RJ12 |
| Headers / Grove / bus pins | Wire to slim P1 PCB |

Feather / Thing Plus boards almost never boost LiPo→5 V. Their “5V” pin is usually **USB only**.

---

## Recommended DevKit: **M5Stack CoreS3** (SKU K128)

https://docs.m5stack.com/en/core/CoreS3  
https://shop.m5stack.com/products/m5stack-cores3-esp32-s3-lotdevelopment-kit

| Feature | On CoreS3 |
|---------|-----------|
| MCU | ESP32-S3, 16 MB Flash, 8 MB PSRAM |
| USB-C | Program + power |
| microSD | Yes |
| Battery | Internal ~500 mAh (+ DinBase can take more / DC) |
| PMU | **AXP2101** (real power management) |
| **5 V out on battery** | **Yes** — Grove / M-Bus **5V** when BUS out enabled |
| UI | Touch screen (handy in the field) |

### Power ICs (CoreS3)

| IC | Role |
|----|------|
| **AXP2101** | Charge, paths, rails, can drive **5 V bus out** from battery |
| AW9523B | Enables `BUS_OUT` / USB OTG direction |

Firmware must enable bus 5 V (M5Unified), e.g. power mode **USB in / BUS out** or `setExtPower` / BUS_OUT_EN as in M5 docs — then Grove **red = 5 V** even on battery.

Grove PORT.A / B / C: **GND · 5V · GPIO · GPIO** → take **5V + GND** to your slim board.

---

## Your slim PCB (still simple)

```
CoreS3 Grove 5V + GND (+ UART/GPIO wires)
        │
        ▼
   TPS2553 ──► RJ12 pin1
   6N137 ×2 ── Request / Data
   RJ12 · ESD · optional INA
```

No charger, no boost, no 3.3 V, no SD, no USB-C on your PCB.

---

## How power behaves (CoreS3)

| Source | MCU runs | Grove/M-Bus **5 V** for eFuse |
|--------|----------|-------------------------------|
| USB-C | Yes | Yes (enable BUS out) |
| Internal battery only | Yes | **Yes** (AXP2101 boost path — enable BUS out) |
| DinBase DC 9–24 V | Yes | Yes |

This matches: **battery in the kit → 5 V out → your eFuse board**. No power bank.

Budget: keep P1 ≤ ~250 mA (TPS2553). Don’t expect amps of 5 V for motors — fine for Ghost.

---

## Fallback if you refuse M5Stack form factor

Stack two proven modules:

1. Any ESP32-S3 DevKit with SD (or Feather + SD wing)  
2. **Adafruit #6106** (bq25185 + **TPS61023 5 V boost**) → `SYS_5V` to TPS2553  

That guarantees LiPo→5 V, but it’s two boards.

---

## Rejected for your requirement

| Board | Why not |
|-------|---------|
| SparkFun Thing Plus ESP32-S3 | No boost; `V_USB` dead on battery-only |
| Adafruit Feather ESP32-S3 alone | Same — USB/BAT, no 5 V boost |
| Most LilyGO “5V” pins | Often mislabeled SYS/battery voltage |

Detail: [ARCHITECTURE.md](ARCHITECTURE.md) · [PARTS_CHECKLIST.md](PARTS_CHECKLIST.md)
