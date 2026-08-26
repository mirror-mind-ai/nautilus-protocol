#!/usr/bin/env python3
"""Validate the DS-002 Nautilus Mission fixture."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nautilus_protocol.identity import format_mission_report, validate_mission  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fixture",
        nargs="?",
        default=str(ROOT / "fixtures" / "nautilus.mission.yaml"),
        help="Path to a Nautilus Mission fixture.",
    )
    args = parser.parse_args()

    validation = validate_mission(args.fixture)
    print(format_mission_report(validation, surface="Nautilus Agentic Protocol mission validation"), end="")
    return 0 if validation.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
