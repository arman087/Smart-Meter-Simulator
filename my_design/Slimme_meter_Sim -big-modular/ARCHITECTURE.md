# Architecture — CoreS3 brain + slim P1

## Locked DevKit

**M5Stack CoreS3** — not SparkFun Thing Plus.

Reason: you need **5 V from battery** for RJ12. Thing Plus cannot do that.

## Split

| CoreS3 | Slim P1 PCB |
|--------|-------------|
| ESP32-S3, USB-C, SD, AXP2101, battery | TPS2553 |
| Grove **5V + GND** → carrier | 6N137 ×2 |
| GPIOs / UART → optos | RJ12 + ESD |
| | Optional INA |

## Power path (what you asked for)

```
Battery (in CoreS3) ──► AXP2101 ──► boost/path ──► Grove 5V
USB-C charge ─────────► AXP2101 ──► charge battery + run system
                                      │
                                      └─► slim PCB TPS2553 → P1
```

Enable BUS 5 V in firmware (M5Unified / BUS_OUT). Verify with meter on Grove red pin while unplugged from USB.

## Slim PCB only

eFuse + optos (+ RJ12). No boost, no charger, no 3.3 V regulator for MCU.
