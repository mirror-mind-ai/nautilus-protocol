#!/usr/bin/env python3
"""Validate the DS-001 Nautilus identity fixture."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nautilus_protocol.identity import format_identity_report, validate_identity  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fixture",
        nargs="?",
        default=str(ROOT / "fixtures" / "nautilus.identity.yaml"),
        help="Path to a Nautilus identity fixture.",
    )
    args = parser.parse_args()

    validation = validate_identity(args.fixture)
    print(format_identity_report(validation, surface="Nautilus Agentic Protocol identity validation"), end="")
    return 0 if validation.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
