"""Minimal Nautilus identity and Mission fixture validation.

DS-001 supports flat identity fixtures. DS-002 adds one nested Mission section
while staying dependency-free and deliberately narrow.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

EXPECTED_IDENTITY = {
    "name": "Nautilus",
    "method_version": "0.1.0-experimental",
    "protocol_version": "0.1.0",
    "schema_version": "0.1.0",
    "grammar_status": "experimental",
    "compatibility": "compatible",
}

EXPECTED_MISSION = {
    "id": "mission-001",
    "title": "Formulate the first Nautilus mission",
    "purpose": "Prove that Nautilus can name a directed intention before execution.",
    "status": "formulated",
}


@dataclass(frozen=True)
class IdentityValidation:
    path: Path
    identity: dict[str, str]
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class MissionValidation:
    path: Path
    identity: dict[str, str]
    mission: dict[str, str]
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


def parse_identity_file(path: str | Path) -> dict[str, str]:
    parsed = _parse_simple_yaml(path)
    identity = {key: value for key, value in parsed.items() if isinstance(value, str)}
    if "mission" in parsed:
        raise ValueError("identity fixture must not include mission section")
    return identity


def parse_mission_file(path: str | Path) -> tuple[dict[str, str], dict[str, str]]:
    parsed = _parse_simple_yaml(path)
    identity = {key: value for key, value in parsed.items() if isinstance(value, str)}
    mission = parsed.get("mission")
    if not isinstance(mission, dict):
        raise ValueError("missing required mission section")
    return identity, mission


def validate_identity(path: str | Path) -> IdentityValidation:
    source = Path(path).expanduser().resolve()
    errors: list[str] = []

    try:
        identity = parse_identity_file(source)
    except Exception as exc:  # noqa: BLE001 - CLI validation should surface parser failures.
        return IdentityValidation(path=source, identity={}, errors=(str(exc),))

    errors.extend(_validate_expected(identity, EXPECTED_IDENTITY, "identity"))

    for key in identity:
        if key not in EXPECTED_IDENTITY:
            errors.append(f"unexpected field for DS-001 identity slice: {key}")

    return IdentityValidation(path=source, identity=identity, errors=tuple(errors))


def validate_mission(path: str | Path) -> MissionValidation:
    source = Path(path).expanduser().resolve()
    errors: list[str] = []

    try:
        identity, mission = parse_mission_file(source)
    except Exception as exc:  # noqa: BLE001 - CLI validation should surface parser failures.
        return MissionValidation(path=source, identity={}, mission={}, errors=(str(exc),))

    errors.extend(_validate_expected(identity, EXPECTED_IDENTITY, "identity"))
    errors.extend(_validate_expected(mission, EXPECTED_MISSION, "mission"))

    for key in identity:
        if key not in EXPECTED_IDENTITY:
            errors.append(f"unexpected identity field for DS-002 mission slice: {key}")
    for key in mission:
        if key not in EXPECTED_MISSION:
            errors.append(f"unexpected mission field for DS-002 mission slice: {key}")

    return MissionValidation(path=source, identity=identity, mission=mission, errors=tuple(errors))


def format_identity_report(validation: IdentityValidation, *, surface: str) -> str:
    lines = [f"{surface}", ""]
    lines.append(f"fixture: {validation.path}")
    lines.append(f"status: {'valid' if validation.valid else 'invalid'}")

    if validation.identity:
        lines.append("")
        for key in EXPECTED_IDENTITY:
            lines.append(f"{key}: {validation.identity.get(key, '<missing>')}")

    _append_errors(lines, validation.errors)
    return "\n".join(lines) + "\n"


def format_mission_report(validation: MissionValidation, *, surface: str) -> str:
    lines = [f"{surface}", ""]
    lines.append(f"fixture: {validation.path}")
    lines.append(f"status: {'valid' if validation.valid else 'invalid'}")

    if validation.identity:
        lines.append("")
        lines.append("identity:")
        for key in EXPECTED_IDENTITY:
            lines.append(f"  {key}: {validation.identity.get(key, '<missing>')}")

    if validation.mission:
        lines.append("")
        lines.append("mission:")
        for key in EXPECTED_MISSION:
            lines.append(f"  {key}: {validation.mission.get(key, '<missing>')}")

    _append_errors(lines, validation.errors)
    return "\n".join(lines) + "\n"


def _validate_expected(actuals: dict[str, str], expected_values: dict[str, str], label: str) -> list[str]:
    errors: list[str] = []
    for key, expected in expected_values.items():
        actual = actuals.get(key)
        if actual is None:
            errors.append(f"missing required {label} field: {key}")
        elif actual != expected:
            errors.append(f"{label}.{key}: expected {expected!r}, got {actual!r}")
    return errors


def _parse_simple_yaml(path: str | Path) -> dict[str, str | dict[str, str]]:
    source = Path(path).expanduser().resolve()
    parsed: dict[str, str | dict[str, str]] = {}
    current_section: str | None = None

    for line_number, raw_line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            raise ValueError(f"line {line_number}: expected 'key: value'")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            raise ValueError(f"line {line_number}: key is required")

        if indent == 0:
            if value == "":
                parsed[key] = {}
                current_section = key
            else:
                parsed[key] = value
                current_section = None
        elif indent == 2 and current_section:
            section = parsed.get(current_section)
            if not isinstance(section, dict):
                raise ValueError(f"line {line_number}: parent section is not a mapping")
            if not value:
                raise ValueError(f"line {line_number}: nested value is required")
            section[key] = value
        else:
            raise ValueError(f"line {line_number}: unsupported indentation for DS-002 fixture")

    return parsed


def _append_errors(lines: list[str], errors: tuple[str, ...]) -> None:
    if errors:
        lines.append("")
        lines.append("errors:")
        for error in errors:
            lines.append(f"- {error}")
