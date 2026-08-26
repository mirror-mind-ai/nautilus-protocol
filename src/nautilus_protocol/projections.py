"""Dependency-free validation for Nautilus Tactical and Strategic projections."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,127}$")
CONTRACT_VERSION = "1.0"
SCHEMA_VERSION = "1"
NAMESPACE = "nautilus-synthesis"


@dataclass(frozen=True)
class ProjectionValidation:
    document: Mapping[str, Any]
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


def load_projection(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("projection document must be a JSON object")
    return value


def validate_tactical(document: Mapping[str, Any]) -> ProjectionValidation:
    errors = _validate_envelope(document, altitude="tactical", projection="tactical")
    content = document.get("content")
    if not isinstance(content, Mapping):
        errors.append("content must be an object")
        return ProjectionValidation(document, tuple(errors))
    _require_exact_keys(content, {"mission", "evidence", "deliverables"}, "content", errors)
    mission = content.get("mission")
    if not isinstance(mission, Mapping):
        errors.append("content.mission must be an object")
    else:
        _require_strings(mission, ("id", "title", "purpose"), "content.mission", errors)
    evidence = _validate_named_records(content.get("evidence"), "content.evidence", {"id", "title", "summary", "sourceReferences"}, errors)
    deliverables = _validate_named_records(content.get("deliverables"), "content.deliverables", {"id", "title", "summary", "evidenceIds", "sourceReferences"}, errors)
    evidence_ids = {item.get("id") for item in evidence}
    for item in deliverables:
        refs = item.get("evidenceIds")
        if not isinstance(refs, list) or not refs or not all(isinstance(value, str) for value in refs):
            errors.append(f"deliverable {item.get('id', '<unknown>')} requires evidenceIds")
        elif not set(refs).issubset(evidence_ids):
            errors.append(f"deliverable {item.get('id', '<unknown>')} references unknown evidence")
    return ProjectionValidation(document, tuple(errors))


def validate_strategic(document: Mapping[str, Any]) -> ProjectionValidation:
    errors = _validate_envelope(document, altitude="strategic", projection="strategic")
    content = document.get("content")
    if not isinstance(content, Mapping):
        errors.append("content must be an object")
        return ProjectionValidation(document, tuple(errors))
    _require_exact_keys(content, {"realizations", "impacts"}, "content", errors)
    impacts = _validate_named_records(content.get("impacts"), "content.impacts", {"id", "title", "summary", "sourceReferences"}, errors)
    realizations = _validate_named_records(content.get("realizations"), "content.realizations", {"id", "title", "summary", "impactIds", "pragmaticValue", "integrativeValue", "sourceReferences"}, errors)
    impact_ids = {item.get("id") for item in impacts}
    for item in realizations:
        refs = item.get("impactIds")
        if not isinstance(refs, list) or not all(isinstance(value, str) for value in refs):
            errors.append(f"realization {item.get('id', '<unknown>')} requires impactIds")
        elif not set(refs).issubset(impact_ids):
            errors.append(f"realization {item.get('id', '<unknown>')} references unknown impacts")
        for lens in ("pragmaticValue", "integrativeValue"):
            value = item.get(lens)
            if not isinstance(value, Mapping):
                errors.append(f"realization {item.get('id', '<unknown>')}.{lens} must be an object")
            else:
                _require_exact_keys(value, {"summary", "sourceReferences"}, lens, errors)
                _require_strings(value, ("summary",), lens, errors)
                _validate_source_references(value.get("sourceReferences"), lens, errors)
    return ProjectionValidation(document, tuple(errors))


def _validate_envelope(document: Mapping[str, Any], *, altitude: str, projection: str) -> list[str]:
    errors: list[str] = []
    expected = {
        "contractVersion": CONTRACT_VERSION,
        "schemaVersion": SCHEMA_VERSION,
        "altitude": altitude,
        "namespace": NAMESPACE,
        "projection": projection,
    }
    for key, value in expected.items():
        if document.get(key) != value:
            errors.append(f"{key} must equal {value!r}")
    for key in ("journeyId", "snapshotId"):
        value = document.get(key)
        if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
            errors.append(f"{key} must be a valid identifier")
    producer = document.get("producer")
    if not isinstance(producer, Mapping) or producer.get("kind") != "extension" or producer.get("id") != NAMESPACE:
        errors.append("producer must identify the nautilus-synthesis extension")
    sources = document.get("sourceSnapshots")
    if not isinstance(sources, list) or not sources:
        errors.append("sourceSnapshots must contain at least the Operational source")
    elif not any(item.get("namespace") == "ariad" and item.get("projection") == "operational" for item in sources if isinstance(item, Mapping)):
        errors.append("sourceSnapshots must reference Ariad Operational")
    return errors


def _validate_named_records(value: Any, label: str, keys: set[str], errors: list[str]) -> list[Mapping[str, Any]]:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty array")
        return []
    records = [item for item in value if isinstance(item, Mapping)]
    if len(records) != len(value):
        errors.append(f"{label} items must be objects")
    seen: set[str] = set()
    for record in records:
        _require_exact_keys(record, keys, label, errors)
        _require_strings(record, ("id", "title", "summary"), label, errors)
        identifier = record.get("id")
        if isinstance(identifier, str):
            if identifier in seen:
                errors.append(f"{label} contains duplicate id {identifier}")
            seen.add(identifier)
        _validate_source_references(record.get("sourceReferences"), label, errors)
    return records


def _validate_source_references(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{label}.sourceReferences must be a non-empty string array")


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], label: str, errors: list[str]) -> None:
    missing = expected - set(value)
    extra = set(value) - expected
    for key in sorted(missing):
        errors.append(f"{label} missing {key}")
    for key in sorted(extra):
        errors.append(f"{label} has unexpected field {key}")


def _require_strings(value: Mapping[str, Any], keys: tuple[str, ...], label: str, errors: list[str]) -> None:
    for key in keys:
        if not isinstance(value.get(key), str) or not value.get(key):
            errors.append(f"{label}.{key} must be a non-empty string")
