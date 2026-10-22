"""Command-line entry point; input data remain local to the user's machine."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from . import __version__
from .analysis import STOError, analyze


def _write_json_atomically(target: Path, body: str) -> None:
    """Replace one report only after its complete contents are written."""
    target.parent.mkdir(parents=True, exist_ok=True)
    temp: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            dir=target.parent, prefix=".scone-sto-audit-", suffix=".tmp",
            delete=False,
        ) as handle:
            temp = handle.name
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, target)
    finally:
        if temp is not None:
            Path(temp).unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit existing SCONE/OpenSim STO outputs (no simulation run)"
    )
    parser.add_argument("files", nargs="+", type=Path, help="Input .sto files")
    parser.add_argument("--columns", nargs="+", required=True, help="Exact channel names")
    parser.add_argument("--start", type=float, help="Inclusive window start")
    parser.add_argument("--end", type=float, help="Inclusive window end")
    parser.add_argument("--output", type=Path, help="Write report JSON instead of stdout")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    try:
        if args.output is not None and any(
            args.output.resolve() == path.resolve() for path in args.files
        ):
            raise STOError("Output must not overwrite an input STO file")
        results = [analyze(path, args.columns, args.start, args.end) for path in args.files]
        report = {
            "tool": "scone-sto-audit",
            "version": __version__,
            "files_analyzed": len(results),
            "note": "Files are not assumed to be independent subjects or conditions.",
            "results": results,
        }
        body = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if args.output is None:
            print(body, end="")
        else:
            _write_json_atomically(args.output, body)
        return 0
    except (STOError, OSError, ValueError, OverflowError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
