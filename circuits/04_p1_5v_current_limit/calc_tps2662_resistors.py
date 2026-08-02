#!/usr/bin/env python3
"""
TPS2662 UVLO / OVP / RILIM resistor calculator
==============================================
Follows TI datasheet §10.2.2 (same algebra as the 18 V / 30 V EVM example).

Divider (IN → R1 → UVLO → R2 → OVP → R3 → RTN):

  V_OV = V_OVPR  * (R1 + R2 + R3) / R3
  V_UV = V_UVLOR * (R1 + R2 + R3) / (R2 + R3)

  IOL  = 6.636 / R_ILIM_kOhm   →   R_ILIM_kOhm = 6.636 / IOL_A

Default targets for Smart Meter Simulator (SYS_5V / P1):
  UVLO = 4 V,  OVP = 9 V,  ILIM options = 250 / 500 / 1000 mA
"""

from __future__ import annotations

# --- design targets (edit these) -------------------------------------------
V_UV = 4.0          # undervoltage lockout rising, volts
V_OV = 9.0          # overvoltage trip rising, volts
V_TH = 1.19         # V(UVLOR) ≈ V(OVPR) from TI example (nom ~1.2 V)

# Pick R3 first (TI style). Higher = less divider current.
R3_CHOSEN_OHM = 30.1e3

# Optional: also size RILIM for these currents (A)
IOL_LIST_A = [0.25, 0.50, 1.00]

V_IN_NOMINAL = 5.0  # for divider current check
LEAKAGE_A = 100e-9  # UVLO/OVP pin leakage (order of)
# ---------------------------------------------------------------------------

# E96 1% decades
_E96 = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 5.11, 5.23, 5.36, 5.49, 5.62,
    5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50,
    7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76,
]


def nearest_e96(r: float) -> float:
    if r <= 0:
        raise ValueError("resistance must be > 0")
    exp = 0
    x = r
    while x < 1.0:
        x *= 10.0
        exp -= 1
    while x >= 10.0:
        x /= 10.0
        exp += 1
    best = min(_E96, key=lambda m: abs(m - x))
    return best * (10.0**exp)


def fmt_ohm(r: float) -> str:
    if r >= 1e6:
        return f"{r/1e6:.3g} MOhm"
    if r >= 1e3:
        return f"{r/1e3:.3g} kOhm"
    return f"{r:.3g} Ohm"


def solve_divider(v_uv: float, v_ov: float, v_th: float, r3: float):
    """Solve R1, R2 given chosen R3 (TI §10.2.2.3 procedure)."""
    if not (0 < v_uv < v_ov):
        raise ValueError("need 0 < V_UV < V_OV")
    # Eq 6: V_OV = v_th * (R1+R2+R3) / R3  →  R1+R2 = R3 * (V_OV/v_th - 1)
    r1_plus_r2 = r3 * (v_ov / v_th - 1.0)
    r_total = r1_plus_r2 + r3
    # Eq 7: V_UV = v_th * R_total / (R2+R3)  →  R2+R3 = R_total * v_th / V_UV
    r2_plus_r3 = r_total * v_th / v_uv
    r2 = r2_plus_r3 - r3
    r1 = r1_plus_r2 - r2
    if r1 <= 0 or r2 <= 0:
        raise ValueError(
            f"non-physical result R1={r1:.3g} R2={r2:.3g}; "
            "try different R3 or V_UV/V_OV (V_UV must be high enough vs V_TH)."
        )
    return r1, r2, r3, r_total


def verify(r1, r2, r3, v_th):
    r_tot = r1 + r2 + r3
    v_ov = v_th * r_tot / r3
    v_uv = v_th * r_tot / (r2 + r3)
    return v_uv, v_ov


def main():
    print("TPS2662 resistor sizing - Smart Meter Simulator P1 path")
    print(f"  targets:  V_UV = {V_UV} V,  V_OV = {V_OV} V,  V_TH = {V_TH} V")
    print(f"  chosen R3 = {fmt_ohm(R3_CHOSEN_OHM)}")
    print()

    r1, r2, r3, r_tot = solve_divider(V_UV, V_OV, V_TH, R3_CHOSEN_OHM)
    print("Exact solve:")
    print(f"  R1 = {fmt_ohm(r1)}  ({r1:.1f} Ohm)")
    print(f"  R2 = {fmt_ohm(r2)}  ({r2:.1f} Ohm)")
    print(f"  R3 = {fmt_ohm(r3)}  ({r3:.1f} Ohm)")

    r1p, r2p, r3p = nearest_e96(r1), nearest_e96(r2), nearest_e96(r3)
    v_uv_a, v_ov_a = verify(r1p, r2p, r3p, V_TH)
    i_div = V_IN_NOMINAL / (r1p + r2p + r3p)

    print()
    print("Closest E96 1% (use these on the PCB):")
    print(f"  R1 = {fmt_ohm(r1p)}")
    print(f"  R2 = {fmt_ohm(r2p)}")
    print(f"  R3 = {fmt_ohm(r3p)}")
    print(f"  -> actual V_UV ~ {v_uv_a:.2f} V")
    print(f"  -> actual V_OV ~ {v_ov_a:.2f} V")
    print(f"  -> divider current @ {V_IN_NOMINAL} V ~ {i_div*1e6:.2f} uA "
          f"(want >> {20*LEAKAGE_A*1e6:.2f} uA)")

    if V_UV < 4.5:
        print()
        print("NOTE: TPS2662 min VIN is ~4.5 V. UVLO=4 V is OK as a pin setpoint,")
        print("      but the chip may not regulate until VIN >= ~4.5 V anyway.")

    print()
    print("R(ILIM) - current limit (independent of UVLO/OVP):")
    print(f"  {'IOL':>8}  {'R_ILIM calc':>12}  {'E96 1%':>10}  {'IOL actual':>10}")
    for iol in IOL_LIST_A:
        r_k = 6.636 / iol
        r_ohm = r_k * 1e3
        r_e = nearest_e96(r_ohm)
        i_act = 6.636 / (r_e / 1e3)
        print(f"  {iol*1e3:6.0f} mA  {fmt_ohm(r_ohm):>12}  {fmt_ohm(r_e):>10}  {i_act*1e3:7.0f} mA")

    print()
    print("Jumper / SP3T wiring reminder:")
    print("  ILIM -- COM --+-- R_250  -- RTN")
    print("                +-- R_500  -- RTN")
    print("                +-- R_1000 -- RTN")


if __name__ == "__main__":
    main()
