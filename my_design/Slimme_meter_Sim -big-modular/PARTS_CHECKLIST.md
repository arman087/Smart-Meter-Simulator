# Parts checklist — DevKit + slim P1 carrier

## Buy (brain)

| # | Item | Link / PN | Notes |
|---|------|-----------|--------|
| D1 | **SparkFun Thing Plus ESP32-S3** | [sparkfun.com](https://www.sparkfun.com/sparkfun-thing-plus-esp32-s3.html) | USB-C, SD, LiPo charge, V_USB header |
| D2 | 1S LiPo JST | Match Thing Plus JST | For portable brain |
| D3 | microSD card | FAT32 | Telegrams |
| D4 | USB-C cable | | Flash / power |

**Alt brain:** Adafruit Feather ESP32-S3 — add SD FeatherWing if you need on-board SD.

---

## Design on slim PCB

| # | Item | Candidate | Notes |
|---|------|-----------|--------|
| C1 | Headers | Feather / Thing Plus compatible | Stack or jumper wires |
| C2 | P1 limit | **TPS2553DBVR** | RILIM ≈ 250–300 mA |
| C3 | Current sense | **INA226** or **INA219** | After TPS2553 |
| C4 | Optos | **6N137** DIP-8 ×2 | Request + Data |
| C5 | RJ12 | 6P6C female | Meter |
| C6 | ESD | TVS on P1 pins | |
| C7 | Optional boost | VBAT→5 V ~1 A | **Only if** battery-only P1 needed |
| C8 | LED / button | ○ | |

---

## Do not put on slim PCB

- ESP32 module / DevKit MCU  
- USB-C for MCU (use Thing Plus)  
- microSD socket (use Thing Plus)  
- Main 3.3 V for MCU  
- Full LiPo charger (unless you abandon Thing Plus charging)

---

## Power modes

| Mode | Carrier 5 V source |
|------|--------------------|
| USB into Thing Plus | **`V_USB`** → TPS2553 |
| Battery only | **`VBAT` → boost → 5 V** on carrier, or USB power bank into Thing Plus |

---

## Rough cart

- [ ] SparkFun Thing Plus ESP32-S3  
- [ ] LiPo + microSD  
- [ ] TPS2553 + INA226/219  
- [ ] 6N137 ×2  
- [ ] RJ12 + headers (Feather pitch)  
- [ ] Optional: boost IC for VBAT→5 V  
