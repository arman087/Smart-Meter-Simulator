#!/usr/bin/env python3
"""
FP6276B Design Calculator
Source: Advanced Analog Technology / Feeling Technology FP6276B datasheet Rev. 0.72
Document: 500kHz 6A High Efficiency Synchronous PWM Boost Converter (12 pages)

All numeric constants below are taken from that datasheet. Component reference
designators match the Typical Application schematic on page 11 (R9 = OCP set).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
import math


# ---------------------------------------------------------------------------
# Datasheet identity / applications
# ---------------------------------------------------------------------------

DATASHEET = {
    "part": "FP6276B",
    "title": "500kHz 6A High Efficiency Synchronous PWM Boost Converter",
    "revision": "0.72",
    "website": "http://www.aat-ic.com/",
    "package": "SOP-8L(EP)",
    "ordering": {
        "part_number": "FP6276BXR-G1",
        "operating_temperature_C": (-40, 85),
        "package": "SOP-8L(EP)",
        "moq": "2500EA",
        "packaging": "Tape & Reel",
    },
    "applications": [
        "Chargers",
        "Handheld Devices",
        "Portable Products",
        "Power Bank",
    ],
    "features": [
        "Current mode with PWM/PSM control",
        "Input voltage range: 2.4V~4.5V",
        "Adjustable Output up to 5.3V",
        "Shutdown current: <1uA",
        "Oscillator frequency: 500KHz",
        "Reference voltage: 0.6V +/-2%",
        "Disconnect load during shutdown",
        "Cycle-by-cycle current limit",
        "Low RDS(on): 40mΩ for both high and low side",
        "Protection: OTP, OCP, SCP",
        "Internal compensation",
        "Internal soft-start: 7ms",
        "Package: SOP-8L(EP)",
    ],
}


# ---------------------------------------------------------------------------
# Pin map (SOP-8L EP) — datasheet page 2
# ---------------------------------------------------------------------------

PIN_TABLE: List[Dict[str, Any]] = [
    {"name": "LX", "no": 1, "io": "I", "description": "Power Switch Output"},
    {"name": "LX", "no": 2, "io": "I", "description": "Power Switch Output"},
    {"name": "VIN", "no": 3, "io": "P", "description": "IC Power Supply"},
    {"name": "EN", "no": 4, "io": "I", "description": "Enable Control (Active High)"},
    {"name": "GND", "no": 5, "io": "P", "description": "IC Ground"},
    {"name": "FB", "no": 6, "io": "I", "description": "Error Amplifier Inverting Input"},
    {
        "name": "OC",
        "no": 7,
        "io": "I",
        "description": "Adjustable Current Limit (resistor must be connected to ground)",
    },
    {"name": "VO", "no": 8, "io": "O", "description": "Output Voltage Pin"},
    {
        "name": "PGND",
        "no": "EP",
        "io": "P",
        "description": "IC Power Ground (Must connect to GND)",
    },
]


# ---------------------------------------------------------------------------
# Absolute maximum ratings — page 4
# ---------------------------------------------------------------------------

ABSOLUTE_MAXIMUM: List[Dict[str, Any]] = [
    {"parameter": "Supply Voltage", "symbol": "VIN", "min": 0, "typ": None, "max": 6, "unit": "V"},
    {"parameter": "LX Voltage", "symbol": "VLX", "min": 0, "typ": None, "max": 6, "unit": "V"},
    {
        "parameter": "EN, FB, OC, VO Voltage",
        "symbol": None,
        "min": 0,
        "typ": None,
        "max": 6,
        "unit": "V",
    },
    {
        "parameter": "Thermal Resistance (SOP-8L EP, Note1)",
        "symbol": "θJA",
        "min": None,
        "typ": None,
        "max": 60,
        "unit": "°C/W",
    },
    {
        "parameter": "Junction Temperature",
        "symbol": "TJ",
        "min": None,
        "typ": None,
        "max": 150,
        "unit": "°C",
    },
    {
        "parameter": "Operating Temperature",
        "symbol": "TOP",
        "min": -40,
        "typ": None,
        "max": 85,
        "unit": "°C",
    },
    {
        "parameter": "Storage Temperature",
        "symbol": "TST",
        "min": -65,
        "typ": None,
        "max": 150,
        "unit": "°C",
    },
    {
        "parameter": "Lead Temperature (soldering, 10 sec)",
        "symbol": None,
        "min": None,
        "typ": None,
        "max": 260,
        "unit": "°C",
    },
]


# ---------------------------------------------------------------------------
# Recommended operating conditions — page 5
# ---------------------------------------------------------------------------

RECOMMENDED_OPERATING: List[Dict[str, Any]] = [
    {"parameter": "Supply Voltage", "symbol": "VIN", "min": 2.4, "typ": None, "max": 4.5, "unit": "V"},
    {
        "parameter": "Operating Temperature Range",
        "symbol": "TA",
        "min": -40,
        "typ": None,
        "max": 85,
        "unit": "°C",
        "conditions": "Ambient Temperature",
    },
]


# ---------------------------------------------------------------------------
# DC electrical characteristics (VIN=3.3V, TA=25°C) — page 5
# ---------------------------------------------------------------------------

DC_ELECTRICAL: List[Dict[str, Any]] = [
    {
        "parameter": "Input Voltage",
        "symbol": "VIN",
        "conditions": "",
        "min": 2.4,
        "typ": None,
        "max": 4.5,
        "unit": "V",
    },
    {
        "parameter": "Under Voltage Lockout",
        "symbol": "VUVLO",
        "conditions": "",
        "min": None,
        "typ": 2.1,
        "max": None,
        "unit": "V",
    },
    {
        "parameter": "UVLO Hysteresis",
        "symbol": None,
        "conditions": "",
        "min": None,
        "typ": 0.1,
        "max": None,
        "unit": "V",
    },
    {
        "parameter": "Quiescent Current",
        "symbol": "ICC",
        "conditions": "VFB=0.65V, No switching",
        "min": None,
        "typ": 280,
        "max": None,
        "unit": "µA",
    },
    {
        "parameter": "Average Supply Current",
        "symbol": "ICC",
        "conditions": "VFB=0.55V, Switching",
        "min": None,
        "typ": 3.6,
        "max": None,
        "unit": "mA",
    },
    {
        "parameter": "Shutdown Current",
        "symbol": "ICC",
        "conditions": "VEN=GND",
        "min": None,
        "typ": 0.1,
        "max": None,
        "unit": "µA",
    },
    {
        "parameter": "Linear Charge Current",
        "symbol": "ICHARGE",
        "conditions": "VOUT < VIN",
        "min": 3,
        "typ": None,
        "max": None,
        "unit": "A",
    },
    {
        "parameter": "Operation Frequency",
        "symbol": "fOSC",
        "conditions": "VFB=0.55V",
        "min": None,
        "typ": 500,
        "max": None,
        "unit": "kHz",
    },
    {
        "parameter": "Maximum Duty Ratio",
        "symbol": "%",
        "conditions": "",
        "min": None,
        "typ": 90,
        "max": None,
        "unit": "%",
    },
    {
        "parameter": "Feedback Voltage",
        "symbol": "VREF",
        "conditions": "VIN=4.5V",
        "min": 0.588,
        "typ": 0.6,
        "max": 0.612,
        "unit": "V",
    },
    {
        "parameter": "Enable Voltage",
        "symbol": "VEN",
        "conditions": "logic high threshold (min)",
        "min": 0.96,
        "typ": None,
        "max": None,
        "unit": "V",
    },
    {
        "parameter": "Shutdown Voltage",
        "symbol": "VEN",
        "conditions": "logic low threshold (max)",
        "min": None,
        "typ": None,
        "max": 0.6,
        "unit": "V",
    },
    {
        "parameter": "Soft-Start Time",
        "symbol": "tSS",
        "conditions": "VIN=4.5V",
        "min": None,
        "typ": 7,
        "max": None,
        "unit": "ms",
    },
    {
        "parameter": "High Side Switch RDS(ON)",
        "symbol": "RON-PMOS",
        "conditions": "",
        "min": None,
        "typ": 40,
        "max": None,
        "unit": "mΩ",
    },
    {
        "parameter": "Low Side Switch RDS(ON)",
        "symbol": "RON-NMOS",
        "conditions": "",
        "min": None,
        "typ": 40,
        "max": None,
        "unit": "mΩ",
    },
    {
        "parameter": "Internal Switch Current Limit",
        "symbol": "IOCP",
        "conditions": "typ (internal)",
        "min": None,
        "typ": 6,
        "max": None,
        "unit": "A",
    },
    {
        "parameter": "Thermal Shutdown Threshold",
        "symbol": "TOTP",
        "conditions": "",
        "min": None,
        "typ": 150,
        "max": None,
        "unit": "°C",
    },
    {
        "parameter": "Thermal Shutdown Hysteresis",
        "symbol": None,
        "conditions": "",
        "min": None,
        "typ": 30,
        "max": None,
        "unit": "°C",
    },
]


# ---------------------------------------------------------------------------
# Design equations & limits — pages 8–9
# ---------------------------------------------------------------------------
# VOUT = 0.6 * (1 + R1/R2)
# IOCP = 180000 / R9 + 0.2     (R9 in ohms, IOCP in amperes)
# R9 range: 37.5k .. 300k  →  IOCP ≈ 5.0A .. 0.8A
# L recommended: 1.5µH .. 4.7µH
# VOUT adjustable up to 5.3V

DESIGN_EQUATIONS = {
    "vout": "VOUT = 0.6 * (1 + R1/R2)",
    "ocp": "IOCP = 180000 / R9 + 0.2",
    "ocp_notes": [
        "Resistor between OC and GND programs peak switch current",
        "R9 must be between 37.5k and 300k",
        "Current limit can be set from 5A to 0.8A",
        "OC pin cannot float — must connect resistor to ground",
        "Keep OC traces short; do not put capacitance on OC",
    ],
    "inductor_notes": [
        "1.5µH to 4.7µH recommended for general application",
        "Consider DCR (lower = better efficiency), Isat, core loss at 500kHz",
        "Avoid inductor saturation",
    ],
    "capacitor_notes": [
        "Low ESR preferred to reduce VOUT ripple",
        "Ceramic X5R / X7R recommended for C1 and C3",
    ],
    "application_notes_page11": [
        "Use ceramic X5R or X7R for C1 and C3",
        "R4 and C5 must be added for reducing spike voltage and EMI",
        "EN voltage must be less than or equal to VIN voltage",
        "OC pin must connect resistor R9 to ground to set current limit",
    ],
}


LAYOUT_RULES: List[str] = [
    "Power traces (GND, LX, VIN) short, direct, and wide",
    "LX switching node: wide and short to reduce EMI",
    "Place C1 near VIN as closely as possible",
    "R1/R2 divider connected to FB directly and closely",
    "Keep FB away from LX",
    "GND of IC, C1, C3, C4 close together on power ground plane; C3/C4 close to VO and PGND(EP)",
    "R4 and C5 close to LX and PGND(EP)",
]


# ---------------------------------------------------------------------------
# Typical application BOM — datasheet page 11
# (designators as printed on the schematic)
# ---------------------------------------------------------------------------

TYPICAL_APPLICATION_BOM: List[Dict[str, Any]] = [
    {
        "ref": "U1",
        "value": "FP6276B",
        "role": "Synchronous boost IC",
        "notes": "SOP-8L(EP); EP = PGND",
    },
    {
        "ref": "L1",
        "value": "3.3µH",
        "role": "Boost inductor",
        "notes": "Within 1.5–4.7µH recommended range",
    },
    {
        "ref": "C1",
        "value": "22µF",
        "role": "Input ceramic capacitor",
        "notes": "X5R/X7R; place near VIN",
    },
    {
        "ref": "C3",
        "value": "22µF",
        "role": "Output ceramic capacitor",
        "notes": "X5R/X7R; close to VO / PGND",
    },
    {
        "ref": "C4",
        "value": "100µF",
        "role": "Output bulk capacitor",
        "notes": "Close to VO / PGND",
    },
    {
        "ref": "R1",
        "value": "75kΩ",
        "role": "FB upper divider",
        "notes": "With R2=10k → VOUT≈5.1V",
    },
    {
        "ref": "R2",
        "value": "10kΩ",
        "role": "FB lower divider",
        "notes": "To GND from FB",
    },
    {
        "ref": "R9",
        "value": "43kΩ",
        "role": "OCP set resistor (OC→GND)",
        "notes": "IOCP = 180000/R9 + 0.2 ≈ 4.39A",
    },
    {
        "ref": "R3",
        "value": "10kΩ",
        "role": "EN series / RC network with C8",
        "notes": "Not the OCP resistor",
    },
    {
        "ref": "C8",
        "value": "1nF",
        "role": "EN filter capacitor",
        "notes": "With R3",
    },
    {
        "ref": "R5",
        "value": "1kΩ",
        "role": "FB feed-forward / filter with C9",
        "notes": "Typical app network on FB path",
    },
    {
        "ref": "C9",
        "value": "150pF",
        "role": "FB feed-forward / filter with R5",
        "notes": "Typical app network on FB path",
    },
    {
        "ref": "R4",
        "value": "1.5Ω",
        "role": "LX snubber resistor",
        "notes": "Must be added (with C5) for spike/EMI",
    },
    {
        "ref": "C5",
        "value": "2.2nF",
        "role": "LX snubber capacitor",
        "notes": "Close to LX and PGND",
    },
]


# Package outline summary — page 12 (mm)
PACKAGE_OUTLINE_MM: Dict[str, Tuple[Optional[float], Optional[float]]] = {
    # symbol: (min, max) ; REF stored as (val, val)
    "A": (1.346, 1.752),
    "A1": (0.050, 0.152),
    "A2": (None, 1.498),  # datasheet shows max only in extract
    "D": (4.800, 4.978),
    "E": (3.810, 3.987),
    "H": (5.791, 6.197),
    "L": (0.406, 1.270),
    "theta_deg": (0.0, 8.0),
    "D1_REF": (3.302, 3.302),
    "E1_REF": (2.413, 2.413),
}


# ---------------------------------------------------------------------------
# E-series helpers (for nearest standard resistors)
# ---------------------------------------------------------------------------

_E24 = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
]

_E96 = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76,
]


def nearest_e_series(ohms: float, series: str = "E96") -> float:
    """Return nearest E24/E96 resistor value to `ohms`."""
    if ohms <= 0:
        raise ValueError("Resistance must be > 0")
    table = _E96 if series.upper() == "E96" else _E24
    exp = math.floor(math.log10(ohms))
    mant = ohms / (10**exp)
    best = min(table, key=lambda m: abs(m - mant))
    return best * (10**exp)


@dataclass
class DesignResult:
    vin_min: float
    vin_nom: float
    vin_max: float
    vout: float
    iout_max: float
    r1_ohms: float
    r2_ohms: float
    r1_e96: float
    r2_e96: float
    vout_actual_e96: float
    r9_ohms: float
    r9_e96: float
    iocp_a: float
    iocp_actual_e96: float
    l_uh: float
    eta_estimate: float
    iin_peak_estimate_a: float
    warnings: List[str]
    bom_suggested: List[Dict[str, Any]]

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FP6276B_Designer:
    """
    Design calculator for the FP6276B boost converter (datasheet Rev. 0.72).

    Important naming (matches Typical Application page 11):
      R1, R2  — FB divider  (VOUT = 0.6 * (1 + R1/R2))
      R9      — OCP set from OC to GND  (IOCP = 180000/R9 + 0.2)
      R3, C8  — EN RC (R3 is NOT OCP)
      R4, C5  — LX snubber (required)
      R5, C9  — FB network in typical app
    """

    def __init__(self) -> None:
        # Core constants
        self.V_REF = 0.6  # V (typ); min 0.588, max 0.612 at VIN=4.5V
        self.V_REF_MIN = 0.588
        self.V_REF_MAX = 0.612
        self.V_REF_TOL = 0.02  # +/-2% feature claim

        self.VIN_MIN = 2.4
        self.VIN_MAX = 4.5
        self.VIN_ABS_MAX = 6.0
        self.VOUT_MAX = 5.3

        self.F_OSC_HZ = 500_000
        self.F_OSC_KHZ = 500
        self.DUTY_MAX = 0.90
        self.T_SOFT_START_S = 0.007
        self.RDS_ON_OHM = 0.040
        self.I_SWITCH_LIMIT_TYP_A = 6.0

        self.V_UVLO = 2.1
        self.V_UVLO_HYST = 0.1
        self.V_EN_HIGH_MIN = 0.96
        self.V_EN_LOW_MAX = 0.6

        self.T_OTP_C = 150
        self.T_OTP_HYST_C = 30

        # OCP set resistor R9 (datasheet calls it R9; equation uses R9)
        self.R9_MIN = 37.5e3
        self.R9_MAX = 300e3
        self.IOCP_AT_R9_MIN = 5.0  # A (datasheet stated range end)
        self.IOCP_AT_R9_MAX = 0.8  # A
        self.OCP_EQ_NUMERATOR = 180_000.0
        self.OCP_EQ_OFFSET = 0.2

        # Inductor
        self.L_MIN_UH = 1.5
        self.L_MAX_UH = 4.7
        self.L_TYP_UH = 3.3

        # Attach full datasheet tables for programmatic use
        self.datasheet = DATASHEET
        self.pin_table = PIN_TABLE
        self.absolute_maximum = ABSOLUTE_MAXIMUM
        self.recommended_operating = RECOMMENDED_OPERATING
        self.dc_electrical = DC_ELECTRICAL
        self.design_equations = DESIGN_EQUATIONS
        self.layout_rules = LAYOUT_RULES
        self.typical_bom = TYPICAL_APPLICATION_BOM
        self.package_outline_mm = PACKAGE_OUTLINE_MM

    # ----- Voltage divider -----

    def calculate_vout(self, r1_ohms: float, r2_ohms: float) -> float:
        """VOUT = 0.6 * (1 + R1/R2)."""
        if r2_ohms <= 0:
            raise ValueError("R2 must be greater than 0 Ohms.")
        return self.V_REF * (1.0 + (r1_ohms / r2_ohms))

    def calculate_r1_for_vout(self, target_vout: float, r2_ohms: float = 10_000.0) -> float:
        """Required R1 for target VOUT with chosen R2."""
        if target_vout <= self.V_REF:
            raise ValueError(f"Target VOUT must be > VREF ({self.V_REF} V).")
        if target_vout > self.VOUT_MAX:
            raise ValueError(f"Target VOUT {target_vout} V exceeds datasheet max {self.VOUT_MAX} V.")
        return r2_ohms * ((target_vout / self.V_REF) - 1.0)

    def calculate_r2_for_vout(self, target_vout: float, r1_ohms: float) -> float:
        """Required R2 for target VOUT with chosen R1."""
        if target_vout <= self.V_REF:
            raise ValueError(f"Target VOUT must be > VREF ({self.V_REF} V).")
        return r1_ohms / ((target_vout / self.V_REF) - 1.0)

    def vout_tolerance_band(
        self, r1_ohms: float, r2_ohms: float, r_tol: float = 0.01
    ) -> Dict[str, float]:
        """
        Approximate VOUT min/max from VREF datasheet min/max and resistor tolerance.
        Worst-case corners (independent).
        """
        r1_hi, r1_lo = r1_ohms * (1 + r_tol), r1_ohms * (1 - r_tol)
        r2_hi, r2_lo = r2_ohms * (1 + r_tol), r2_ohms * (1 - r_tol)
        v_nom = self.V_REF * (1 + r1_ohms / r2_ohms)
        v_max = self.V_REF_MAX * (1 + r1_hi / r2_lo)
        v_min = self.V_REF_MIN * (1 + r1_lo / r2_hi)
        return {"vout_nom": v_nom, "vout_min": v_min, "vout_max": v_max}

    # ----- OCP (R9) -----

    def calculate_ocp_current(self, r9_ohms: float, warn: bool = True) -> float:
        """IOCP = 180000/R9 + 0.2  (Amperes)."""
        if r9_ohms <= 0:
            raise ValueError("R9 must be > 0.")
        if warn and not (self.R9_MIN <= r9_ohms <= self.R9_MAX):
            print(
                f"Warning: R9 ({r9_ohms / 1e3:.3f} kΩ) outside recommended "
                f"{self.R9_MIN / 1e3:.1f}k–{self.R9_MAX / 1e3:.0f}k range."
            )
        return (self.OCP_EQ_NUMERATOR / r9_ohms) + self.OCP_EQ_OFFSET

    def calculate_r9_for_ocp(self, target_iocp: float, warn: bool = True) -> float:
        """R9 for desired peak switch current limit (A)."""
        if target_iocp <= self.OCP_EQ_OFFSET:
            raise ValueError(
                f"Target IOCP must be > {self.OCP_EQ_OFFSET} A due to equation offset."
            )
        r9 = self.OCP_EQ_NUMERATOR / (target_iocp - self.OCP_EQ_OFFSET)
        if warn and not (self.R9_MIN <= r9 <= self.R9_MAX):
            print(
                f"Warning: Calculated R9 ({r9 / 1e3:.2f} kΩ) outside "
                f"{self.R9_MIN / 1e3:.1f}k–{self.R9_MAX / 1e3:.0f}k "
                f"(datasheet IOCP programming window ≈ {self.IOCP_AT_R9_MAX}–{self.IOCP_AT_R9_MIN} A)."
            )
        return r9

    # Backwards-compatible aliases (older drafts called the OCP resistor R3)
    def calculate_r3_for_ocp(self, target_iocp: float) -> float:
        """Alias: datasheet OCP resistor is R9, not R3."""
        return self.calculate_r9_for_ocp(target_iocp)

    # ----- Duty / current estimates (engineering, not datasheet formulas) -----

    def duty_ideal(self, vin: float, vout: float) -> float:
        """Ideal boost duty D = 1 - VIN/VOUT (CCM continuous)."""
        if vout <= 0:
            raise ValueError("VOUT must be > 0")
        return max(0.0, min(1.0, 1.0 - (vin / vout)))

    def estimate_input_current(self, vout: float, iout: float, vin: float, eta: float = 0.90) -> float:
        """IIN_avg ≈ (VOUT * IOUT) / (VIN * η)."""
        if vin <= 0 or eta <= 0:
            raise ValueError("VIN and eta must be > 0")
        return (vout * iout) / (vin * eta)

    def estimate_inductor_peak(
        self,
        vin: float,
        vout: float,
        iout: float,
        l_uh: float,
        eta: float = 0.90,
    ) -> float:
        """
        Rough CCM peak inductor / switch current:
          IIN_avg = VOUT*IOUT/(VIN*η)
          ΔIL = VIN*D / (f*L)
          IL_peak ≈ IIN_avg + ΔIL/2
        Use to choose Isat and set IOCP with margin.
        """
        d = self.duty_ideal(vin, vout)
        iin = self.estimate_input_current(vout, iout, vin, eta)
        l_h = l_uh * 1e-6
        delta_il = (vin * d) / (self.F_OSC_HZ * l_h) if l_h > 0 else float("inf")
        return iin + 0.5 * delta_il

    def suggest_ocp_from_load(
        self,
        vin_min: float,
        vout: float,
        iout_max: float,
        l_uh: float = 3.3,
        eta: float = 0.90,
        margin: float = 1.25,
    ) -> Dict[str, float]:
        """Suggest IOCP and R9 from worst-case (VIN_min) peak current + margin."""
        il_peak = self.estimate_inductor_peak(vin_min, vout, iout_max, l_uh, eta)
        iocp = il_peak * margin
        # Clamp into programmable window if possible
        iocp_clamped = min(max(iocp, self.IOCP_AT_R9_MAX), self.IOCP_AT_R9_MIN)
        r9 = self.calculate_r9_for_ocp(iocp_clamped, warn=False)
        return {
            "il_peak_est_a": il_peak,
            "iocp_target_a": iocp,
            "iocp_programmed_a": iocp_clamped,
            "r9_ohms": r9,
        }

    # ----- Full design recipe -----

    def design(
        self,
        vout: float = 5.0,
        iout_max: float = 0.5,
        vin_min: float = 3.0,
        vin_nom: float = 3.7,
        vin_max: float = 4.2,
        r2_ohms: float = 10_000.0,
        l_uh: float = 3.3,
        eta: float = 0.90,
        ocp_margin: float = 1.30,
        series: str = "E96",
    ) -> DesignResult:
        """
        Produce a complete resistor/inductor suggestion for a LiPo → 5V boost
        (or other VOUT ≤ 5.3V) design, using datasheet equations + typical BOM.
        """
        warnings: List[str] = []

        if not (self.VIN_MIN <= vin_min <= vin_max <= self.VIN_MAX):
            warnings.append(
                f"VIN window {vin_min}–{vin_max} V should sit inside "
                f"{self.VIN_MIN}–{self.VIN_MAX} V recommended operating range."
            )
        if vout > self.VOUT_MAX:
            raise ValueError(f"VOUT {vout} > datasheet max {self.VOUT_MAX} V")
        if not (self.L_MIN_UH <= l_uh <= self.L_MAX_UH):
            warnings.append(
                f"L={l_uh}µH outside recommended {self.L_MIN_UH}–{self.L_MAX_UH}µH."
            )
        if vin_max >= vout:
            warnings.append(
                "VIN_max >= VOUT: boost may enter linear-charge / passthrough region "
                f"(ICHARGE ≥ 3A when VOUT<VIN per datasheet)."
            )

        r1 = self.calculate_r1_for_vout(vout, r2_ohms)
        r1_e = nearest_e_series(r1, series)
        r2_e = nearest_e_series(r2_ohms, series)
        vout_e = self.calculate_vout(r1_e, r2_e)

        ocp = self.suggest_ocp_from_load(vin_min, vout, iout_max, l_uh, eta, ocp_margin)
        r9 = ocp["r9_ohms"]
        r9_e = nearest_e_series(r9, series)
        # Prefer staying inside R9 window after E-series snap
        if r9_e < self.R9_MIN:
            r9_e = nearest_e_series(self.R9_MIN, series)
            warnings.append("R9 E-series snapped below min; clamped toward 37.5k.")
        if r9_e > self.R9_MAX:
            r9_e = nearest_e_series(self.R9_MAX, series)
            warnings.append("R9 E-series snapped above max; clamped toward 300k.")
        iocp_e = self.calculate_ocp_current(r9_e, warn=False)

        d_worst = self.duty_ideal(vin_min, vout)
        if d_worst > self.DUTY_MAX:
            warnings.append(
                f"Ideal duty at VIN_min is {d_worst*100:.1f}% > max duty {self.DUTY_MAX*100:.0f}%."
            )

        il_peak = ocp["il_peak_est_a"]
        if il_peak > self.I_SWITCH_LIMIT_TYP_A:
            warnings.append(
                f"Estimated IL_peak {il_peak:.2f} A exceeds typ internal switch limit "
                f"{self.I_SWITCH_LIMIT_TYP_A} A."
            )

        bom = [
            {"ref": "U1", "value": "FP6276BXR-G1", "notes": "SOP-8L(EP)"},
            {"ref": "L1", "value": f"{l_uh}µH", "notes": f"Isat > {il_peak*1.2:.2f} A; low DCR"},
            {"ref": "C1", "value": "22µF", "notes": "X5R/X7R ceramic near VIN (typ app)"},
            {"ref": "C3", "value": "22µF", "notes": "X5R/X7R ceramic near VO (typ app)"},
            {"ref": "C4", "value": "100µF", "notes": "Bulk near VO/PGND (typ app)"},
            {"ref": "R1", "value": f"{r1_e:.4g}Ω", "notes": f"FB upper; target VOUT={vout}V"},
            {"ref": "R2", "value": f"{r2_e:.4g}Ω", "notes": "FB lower"},
            {"ref": "R9", "value": f"{r9_e:.4g}Ω", "notes": f"OCP ≈ {iocp_e:.2f} A; OC→GND, no cap"},
            {"ref": "R3", "value": "10kΩ", "notes": "EN RC with C8 (typ app)"},
            {"ref": "C8", "value": "1nF", "notes": "EN filter (typ app)"},
            {"ref": "R5", "value": "1kΩ", "notes": "FB network with C9 (typ app)"},
            {"ref": "C9", "value": "150pF", "notes": "FB network with R5 (typ app)"},
            {"ref": "R4", "value": "1.5Ω", "notes": "LX snubber — required"},
            {"ref": "C5", "value": "2.2nF", "notes": "LX snubber — close to LX/PGND"},
        ]

        return DesignResult(
            vin_min=vin_min,
            vin_nom=vin_nom,
            vin_max=vin_max,
            vout=vout,
            iout_max=iout_max,
            r1_ohms=r1,
            r2_ohms=r2_ohms,
            r1_e96=r1_e,
            r2_e96=r2_e,
            vout_actual_e96=vout_e,
            r9_ohms=r9,
            r9_e96=r9_e,
            iocp_a=ocp["iocp_programmed_a"],
            iocp_actual_e96=iocp_e,
            l_uh=l_uh,
            eta_estimate=eta,
            iin_peak_estimate_a=il_peak,
            warnings=warnings,
            bom_suggested=bom,
        )

    # ----- Reporting -----

    def print_datasheet_tables(self) -> None:
        print("=== FP6276B DATASHEET EXTRACT (Rev. 0.72) ===")
        print(f"Part: {self.datasheet['part']} — {self.datasheet['title']}")
        print("Applications:", ", ".join(self.datasheet["applications"]))
        print("\n-- Pins --")
        for p in self.pin_table:
            print(f"  {p['no']:>3}  {p['name']:<5}  {p['io']}  {p['description']}")
        print("\n-- Recommended operating --")
        for r in self.recommended_operating:
            print(f"  {r['parameter']}: {r['min']} .. {r['max']} {r['unit']}")
        print("\n-- Key DC specs --")
        for r in self.dc_electrical:
            print(
                f"  {r['parameter']}: min={r['min']} typ={r['typ']} max={r['max']} "
                f"{r['unit']}  ({r['conditions']})"
            )
        print("\n-- Equations --")
        print(" ", self.design_equations["vout"])
        print(" ", self.design_equations["ocp"])
        print("\n-- Typical Application BOM (page 11) --")
        for c in self.typical_bom:
            print(f"  {c['ref']:<4} {c['value']:<10} {c['role']:<28} {c['notes']}")

    def verify_typical_application(self) -> Dict[str, float]:
        """Check page-11 example: R1=75k, R2=10k, R9=43k."""
        vout = self.calculate_vout(75_000, 10_000)
        iocp = self.calculate_ocp_current(43_000, warn=False)
        return {"vout_typical_app": vout, "iocp_typical_app": iocp}


# --- Example Usage ---
if __name__ == "__main__":
    import sys

    # Windows consoles are often cp1252; keep Ω/µ printable
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    designer = FP6276B_Designer()

    print("--- FP6276B Design Calculator (datasheet Rev. 0.72) ---\n")
    designer.print_datasheet_tables()

    print("\n=== Typical Application Verification (page 11) ===")
    typ = designer.verify_typical_application()
    print(f"R1=75k, R2=10k → VOUT = {typ['vout_typical_app']:.3f} V  (expect ~5.10 V)")
    print(f"R9=43k → IOCP = {typ['iocp_typical_app']:.3f} A  (expect ~4.39 A)")

    print("\n=== Design for Smart Meter Simulator (LiPo → 5.0 V) ===")
    # Ghost ~250 mA + LCD ~100 mA @ 5V + headroom → design ~0.6–0.8 A out
    result = designer.design(
        vout=5.0,
        iout_max=0.8,
        vin_min=3.0,
        vin_nom=3.7,
        vin_max=4.2,
        r2_ohms=10_000,
        l_uh=3.3,
        eta=0.90,
        ocp_margin=1.30,
    )
    print(f"Ideal R1 = {result.r1_ohms/1000:.3f} kΩ → E96 {result.r1_e96/1000:.3f} kΩ")
    print(f"R2 E96   = {result.r2_e96/1000:.3f} kΩ")
    print(f"VOUT with E96 pair = {result.vout_actual_e96:.3f} V")
    print(f"IL_peak est @ VIN_min = {result.iin_peak_estimate_a:.2f} A")
    print(f"R9 ideal = {result.r9_ohms/1000:.2f} kΩ → E96 {result.r9_e96/1000:.2f} kΩ")
    print(f"IOCP with E96 R9 = {result.iocp_actual_e96:.2f} A")
    if result.warnings:
        print("Warnings:")
        for w in result.warnings:
            print(" -", w)
    print("\nSuggested BOM:")
    for row in result.bom_suggested:
        print(f"  {row['ref']:<4} {row['value']:<12} {row['notes']}")

    print("\n=== Quick API checks (compatible with earlier draft) ===")
    print(f"VOUT(R1=73k,R2=10k) = {designer.calculate_vout(73000, 10000):.3f} V")
    print(f"R1 for 5.0V, R2=10k = {designer.calculate_r1_for_vout(5.0, 10000)/1000:.2f} kΩ")
    print(f"R9 for IOCP=2.0A = {designer.calculate_r9_for_ocp(2.0)/1000:.2f} kΩ")
