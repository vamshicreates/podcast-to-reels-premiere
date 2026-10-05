#!/usr/bin/env python3
"""Compile an approved timeline spec using premiere-editing-dna on macOS or Windows."""

from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path, help="Approved timeline_spec.json")
    parser.add_argument("--builder", required=True, type=Path,
                        help="Installed premiere-editing-dna/scripts/build_premiere_sequence.py")
    args = parser.parse_args()
    if not args.spec.is_file() or not args.builder.is_file():
        parser.error("--spec and --builder must point to existing files")

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    # Calling the compiler function directly avoids the dependency's CLI help-text
    # formatting bug in versions that contain an unescaped percent sign.
    builder = runpy.run_path(str(args.builder.resolve()))["build_sequence_xml"]
    result = builder(spec)
    if result.get("status") != "success":
        raise SystemExit(f"Premiere compiler did not succeed: {result}")
    if float(result.get("durationSec", 120)) >= 120:
        raise SystemExit(f"Compiled timeline is not under 120 seconds: {result}")
    if not Path(result["outputXml"]).is_file():
        raise SystemExit("Premiere XML was not written")
    if spec.get("captions") and not Path(result.get("outputSrt") or "").is_file():
        raise SystemExit("Premiere SRT was not written")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
