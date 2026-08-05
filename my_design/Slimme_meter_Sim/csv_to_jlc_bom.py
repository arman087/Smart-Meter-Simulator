#!/usr/bin/env python3
"""
Convert KiCad / EasyEDA CSV BOMs in this folder to JLCPCB Excel BOMs.

Double-click or run:
  python csv_to_jlc_bom.py

Finds every *.csv next to this script and writes <same_name>_JLCPCB.xlsx
with columns JLCPCB SMT assembly expects.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

try:
    from openpyxl import Workbook
except ImportError:
    print("Missing openpyxl. Install once with:")
    print("  pip install openpyxl")
    try:
        input("Press Enter to close...")
    except EOFError:
        pass
    sys.exit(1)


# JLCPCB BOM headers (SMT assembly upload)
JLC_HEADERS = ["Comment", "Designator", "Footprint", "LCSC Part #", "Quantity"]

# KiCad / EasyEDA export column names → internal keys
COL_ALIASES = {
    "reference": "designator",
    "designator": "designator",
    "qty": "qty",
    "quantity": "qty",
    "value": "value",
    "comment": "comment",
    "footprint": "footprint",
    "mpn": "mpn",
    "manufacturer": "manufacturer",
    "lcsc part": "lcsc",
    "lcsc part #": "lcsc",
    "lcsc": "lcsc",
    "dnp": "dnp",
    "exclude from bom": "exclude_bom",
}


def norm_header(name: str) -> str:
    return " ".join(name.strip().lower().replace("_", " ").split())


def map_row(headers: list[str], row: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for h, cell in zip(headers, row):
        key = COL_ALIASES.get(norm_header(h))
        if key:
            out[key] = (cell or "").strip()
    return out


def clean_footprint(fp: str) -> str:
    # EasyEDA:C0603 → C0603
    if ":" in fp:
        return fp.split(":", 1)[1].strip()
    return fp


def should_skip(part: dict[str, str]) -> bool:
    if part.get("exclude_bom", "").lower() in {"yes", "true", "1", "y"}:
        return True
    if part.get("dnp", "").lower() in {"yes", "true", "1", "y", "dnp"}:
        return True
    designator = part.get("designator", "")
    value = part.get("value", "")
    if not designator:
        return True
    # Mounting holes / empty placeholders
    if value in {"~", ""} and designator.upper().startswith("H"):
        return True
    return False


def to_jlc_rows(csv_path: Path) -> list[list[str]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            return []

        rows: list[list[str]] = []
        for raw in reader:
            if not any(c.strip() for c in raw):
                continue
            part = map_row(headers, raw)
            if should_skip(part):
                continue

            lcsc = part.get("lcsc", "")
            comment = part.get("comment") or part.get("mpn") or part.get("value") or ""
            designator = part.get("designator", "")
            footprint = clean_footprint(part.get("footprint", ""))
            qty = part.get("qty") or str(max(1, designator.count(",") + 1))

            rows.append([comment, designator, footprint, lcsc, qty])
        return rows


def write_xlsx(path: Path, rows: list[list[str]]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "BOM"
    ws.append(JLC_HEADERS)
    for row in rows:
        ws.append(row)

    # Comfortable column widths
    widths = [36, 40, 36, 14, 10]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + i)].width = w

    wb.save(path)


def pause() -> None:
    # Keep window open on double-click; skip in pipes/CI
    try:
        if sys.stdin is not None and sys.stdin.isatty():
            input("Press Enter to close...")
    except EOFError:
        pass


def main() -> int:
    folder = Path(__file__).resolve().parent
    csv_files = sorted(folder.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in:\n  {folder}")
        pause()
        return 1

    print(f"Folder: {folder}\n")
    ok = 0
    for csv_path in csv_files:
        out_path = csv_path.with_name(f"{csv_path.stem}_JLCPCB.xlsx")
        try:
            rows = to_jlc_rows(csv_path)
            write_xlsx(out_path, rows)
            missing = sum(1 for r in rows if not r[3])
            print(f"OK  {csv_path.name}")
            print(f" -> {out_path.name}  ({len(rows)} parts"
                  + (f", {missing} without LCSC" if missing else "")
                  + ")")
            ok += 1
        except Exception as e:
            print(f"FAIL {csv_path.name}: {e}")

    print(f"\nDone: {ok}/{len(csv_files)} converted.")
    pause()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
