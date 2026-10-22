"""Strict scalar STO parsing and sampled-point descriptive statistics.

This module does not execute SCONE, control optimization, infer units, or
perform inferential statistics. Data are assumed to be precomputed.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any


class STOError(ValueError):
    """Input rejected because its structure or analysis semantics are invalid."""


def read_sto(path: Path) -> dict[str, Any]:
    """Read a scalar, whitespace-delimited STO file with an ``endheader`` line.

    Fail closed on malformed metadata, nonnumeric values, nonfinite values,
    inconsistent table width, and nonincreasing timestamps.
    """
    path = Path(path)
    if not path.is_file():
        raise STOError(f"Input not found: {path}")
    try:
        raw = path.read_bytes()
        lines = raw.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError as exc:
        raise STOError("STO must be UTF-8 text") from exc
    except OSError as exc:
        raise STOError(f"Input could not be read: {path}") from exc

    header_at = next(
        (i for i, line in enumerate(lines) if line.strip().lower() == "endheader"),
        None,
    )
    if header_at is None:
        raise STOError("Missing endheader marker")

    metadata: dict[str, str] = {}
    for line in lines[:header_at]:
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if "=" in text:
            key, value = text.split("=", 1)
        else:
            parts = text.split(None, 1)
            if len(parts) < 2 or parts[0].lower() not in {
                "nrows", "ncolumns", "datarows", "datacolumns", "indegrees"
            }:
                continue
            key, value = parts
        key = key.strip().lower()
        value = value.strip()
        if key in metadata:
            raise STOError(f"Duplicate header key: {key}")
        metadata[key] = value

    remaining = [
        line.strip()
        for line in lines[header_at + 1:]
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(remaining) < 2:
        raise STOError("Missing column names or data rows")
    names = remaining[0].split()
    if (
        len(names) < 2
        or names[0].lower() != "time"
        or len({name.lower() for name in names}) != len(names)
    ):
        raise STOError("First column must be time; columns must be unique")

    rows: list[list[float]] = []
    previous_time = -math.inf
    for row_number, line in enumerate(remaining[1:], 1):
        tokens = line.split()
        if len(tokens) != len(names):
            raise STOError(
                f"Row {row_number}: expected {len(names)} values, found {len(tokens)}"
            )
        try:
            row = [float(token) for token in tokens]
        except ValueError as exc:
            raise STOError(f"Row {row_number}: nonnumeric field") from exc
        if not all(math.isfinite(value) for value in row):
            raise STOError(f"Row {row_number}: NaN or infinity")
        if row[0] <= previous_time:
            raise STOError(f"Row {row_number}: time must be strictly increasing")
        previous_time = row[0]
        rows.append(row)

    for key, observed in (
        ("nrows", len(rows)),
        ("datarows", len(rows)),
        ("ncolumns", len(names)),
        ("datacolumns", len(names)),
    ):
        if key in metadata:
            try:
                expected = int(metadata[key])
            except ValueError as exc:
                raise STOError(f"Invalid {key} metadata") from exc
            if expected != observed:
                raise STOError(f"Header {key}={expected}, observed {observed}")
    if "indegrees" in metadata and metadata["indegrees"].lower() not in {
        "yes", "no", "true", "false", "0", "1"
    }:
        raise STOError("Ambiguous inDegrees metadata")

    return {
        "columns": names,
        "rows": rows,
        "metadata": metadata,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def analyze(
    path: Path,
    columns: list[str],
    start: float | None = None,
    end: float | None = None,
) -> dict[str, Any]:
    """Calculate source-unit sample summaries for exact selected channels.

    Window boundaries are inclusive. Neither interpolation nor unit
    conversion is performed. ``range`` means max-minus-min, not a
    validated biomechanical range of motion for arbitrary channels.
    """
    if not columns or len(set(columns)) != len(columns):
        raise STOError("Provide at least one distinct column")
    table = read_sto(path)
    names, rows = table["columns"], table["rows"]
    missing = [column for column in columns if column not in names or column == names[0]]
    if missing:
        raise STOError("Missing or invalid value columns: " + ", ".join(missing))
    if (start is not None and not math.isfinite(start)) or (
        end is not None and not math.isfinite(end)
    ):
        raise STOError("Window bounds must be finite")
    lo = rows[0][0] if start is None else start
    hi = rows[-1][0] if end is None else end
    if lo >= hi or lo < rows[0][0] or hi > rows[-1][0]:
        raise STOError("Window must be nonempty and within the recorded time domain")
    window = [row for row in rows if lo <= row[0] <= hi]
    if not window:
        raise STOError("Window contains no sampled rows")

    metrics: dict[str, dict[str, float]] = {}
    for column in columns:
        position = names.index(column)
        values = [row[position] for row in window]
        minimum, maximum = min(values), max(values)
        # Divide before summing to avoid overflow when the arithmetic mean
        # is finite but the raw sum is not.
        mean = math.fsum(value / len(values) for value in values)
        width = maximum - minimum
        if not (math.isfinite(width) and math.isfinite(mean)):
            raise STOError(f"Derived metric is nonfinite for column {column}")
        metrics[column] = {
            "min": minimum,
            "max": maximum,
            "range": width,
            "peak_absolute": max(abs(value) for value in values),
            "mean_sampled": mean,
        }
    return {
        "input_file": Path(path).name,
        "input_sha256": table["sha256"],
        "window_time": {"start": lo, "end": hi, "samples": len(window)},
        "time_units_assumed": "seconds (verify against the source model)",
        "inDegrees_header": table["metadata"].get("indegrees", "unspecified"),
        "values_in_source_units": True,
        "note": (
            "Sampled-point summaries only. No interpolation, unit conversion, "
            "normalization or biological inference."
        ),
        "metrics": metrics,
    }
