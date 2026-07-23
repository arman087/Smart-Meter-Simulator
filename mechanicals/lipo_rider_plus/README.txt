LIPO RIDER PLUS — DAUGHTERBOARD (CHOSEN POWER)
==============================================

Product
-------
Seeed Studio Lipo Rider Plus (SKU 106990290)
Wiki: https://wiki.seeedstudio.com/Lipo-Rider-Plus/
Buy:  Seeed / distributors — search "Lipo Rider Plus"

This is the project power solution: MCU charger/booster as a daughterboard.
Draw your own footprint if you prefer; files below are a reference.

Mounting on YOUR PCB
--------------------
Files in this folder:

1) Seeed_Lipo_Rider_Plus.kicad_mod
   KiCad footprint for the main board:
   - Board outline (~40.9 × 28.0 mm) from official Eagle .brd
   - 4× M3 clearance holes (3.2 mm) at official positions
   - 1×8 2.54 mm header pads matching J3

   How to use in KiCad:
   - Preferences → Manage Footprint Libraries → add this folder
     (or copy .kicad_mod into your project .pretty)
   - Place footprint; wire pads:
       1 USB   (sense only / optional)
       2 GND
       3 BAT   (optional monitor)
       4 GND
       5 5V    → SYS_5V
       6 GND
       7 EN    (pull to GND to cut 5V; leave open for ON)
       8 3V3   → VCC_3V3

   Stacking tip: solder a male 1×8 header on the Lipo Rider bottom,
   female 1×8 on the main PCB (or wire pads with short jumpers).
   Use M3 standoffs in the four holes.

2) Lipo_Rider_Plus_box.wrl
   Crude 3D placeholder box for KiCad 3D view (not accurate connectors).

3) sch_pcb/Lipo Rider Plus.brd + .sch
   Official Seeed Eagle design (source of outline / holes / header).

4) pinout.jpg / size.jpg / front.jpg
   Official photos from SeeedDocument/Lipo-Rider-Plus on GitHub.

Official / community 3D
-----------------------
- Official mechanical source: Eagle .brd in sch_pcb/ (best for holes).
- Community STEP (used by Printables case authors): search GrabCAD for
  "Lipo Rider Plus" (Joel vL). GrabCAD needs a free account to download.
- 3D-print case reference (mentions that STEP):
  https://www.printables.com/model/569285-seeed-lipo-rider-plus-case

There is NO official Seeed STEP in the public zip we found.
Use GrabCAD STEP for enclosure; use our .kicad_mod for PCB mounting.

Dimensions (from Eagle)
-----------------------
Board outline: 0 … 40.877 mm (X), 2.5 … 27.98 mm (Y) ≈ 41 × 25.5 mm body
Seeed marketing size: 2.5 cm × 4.1 cm

Mounting holes (drill 3.0 mm on module):
  (10.778, 5.04), (10.778, 25.567), (38.337, 5.04), (38.337, 25.567)

Header J3 centre: (23.114, 3.937), 8 pins @ 2.54 mm along X
