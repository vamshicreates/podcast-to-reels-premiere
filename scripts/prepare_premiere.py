#!/usr/bin/env python3
"""Gate approved reel plans and write Premiere Editing DNA timeline specs."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(message)


def seconds(value: object, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        fail(f"{label} must be a number")
    if not math.isfinite(number):
        fail(f"{label} must be finite")
    return number


def safe_id(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", value):
        fail(f"Invalid reel ID: {value!r}")
    return value


def media_duration(path: Path) -> float:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            check=True, capture_output=True, text=True, timeout=30,
        )
        return float(result.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        fail(f"Cannot read media duration for {path}: {exc}")


def prepare(reel: dict, output_dir: Path) -> tuple[Path, float]:
    reel_id = safe_id(reel.get("id"))
    segments = reel.get("segments")
    if not isinstance(segments, list) or not segments:
        fail(f"{reel_id}: at least one segment is required")

    fps = seconds(reel.get("fps", 30), "fps")
    if fps <= 0:
        fail(f"{reel_id}: fps must be positive")
    timebase = round(fps)  # Matches premiere-editing-dna's XML compiler.
    cursor_frames = 0
    ar = []
    captions = []
    durations: dict[Path, float] = {}
    for index, segment in enumerate(segments, 1):
        if not isinstance(segment, dict):
            fail(f"{reel_id}: segment {index} must be an object")
        source = Path(str(segment.get("path", ""))).expanduser()
        if not source.is_absolute() or not source.is_file():
            fail(f"{reel_id}: segment {index} needs an existing absolute media path")
        start = seconds(segment.get("inSec"), f"{reel_id} segment {index} inSec")
        end = seconds(segment.get("outSec"), f"{reel_id} segment {index} outSec")
        if start < 0 or end <= start:
            fail(f"{reel_id}: invalid range in segment {index}")
        if source not in durations:
            durations[source] = media_duration(source)
        if end > durations[source] + 0.001:
            fail(f"{reel_id}: segment {index} ends after source media ({durations[source]:.3f}s)")
        in_frame = round(start * timebase)
        out_frame = round(end * timebase)
        if out_frame <= in_frame:
            fail(f"{reel_id}: segment {index} is shorter than one output frame")
        start_frame = cursor_frames
        ar.append({
            "name": f"{reel_id}_A{index:02d}", "path": str(source),
            "inSec": start, "outSec": end, "startSec": round(start_frame / timebase, 6),
            "scale": seconds(segment.get("scale", 100), "scale"),
            "gainDb": seconds(segment.get("gainDb", 0), "gainDb"),
        })
        for cap_index, cap in enumerate(segment.get("captions", []), 1):
            c_start = seconds(cap.get("startSec"), "caption startSec")
            c_end = seconds(cap.get("endSec"), "caption endSec")
            line = cap.get("text", "")
            if c_start < start or c_end > end or c_end <= c_start or not isinstance(line, str) or not line.strip():
                fail(f"{reel_id}: caption {cap_index} in segment {index} is outside its source range or empty")
            captions.append({
                "startSec": round((start_frame + round(c_start * timebase) - in_frame) / timebase, 6),
                "endSec": round((start_frame + round(c_end * timebase) - in_frame) / timebase, 6),
                "text": line.strip(),
            })
        cursor_frames += out_frame - in_frame

    cursor = cursor_frames / timebase
    if cursor_frames >= 120 * timebase:
        fail(f"{reel_id}: planned duration {cursor:.3f}s must be below 120s")
    if cursor_frames <= 0:
        fail(f"{reel_id}: empty reel")

    target = output_dir / reel_id
    spec = {
        "sequence": {
            "name": str(reel.get("title") or reel_id),
            "width": int(reel.get("width", 1080)),
            "height": int(reel.get("height", 1920)),
            "fps": fps,
        },
        "outputXml": str(target / f"{reel_id}.xml"),
        "outputSrt": str(target / f"{reel_id}.srt"),
        "v1_aroll": ar,
        "captions": sorted(captions, key=lambda item: item["startSec"]),
    }
    for key in ("v2_broll", "v3_overlays", "a2_sfx", "a3_bgm", "markers"):
        value = reel.get(key, [])
        if not isinstance(value, list):
            fail(f"{reel_id}: {key} must be an array")
        for index, item in enumerate(value, 1):
            if not isinstance(item, dict):
                fail(f"{reel_id}: {key} item {index} must be an object")
            at = seconds(item.get("timeSec" if key == "markers" else "startSec", 0), f"{key} start")
            if at < 0 or at >= cursor:
                fail(f"{reel_id}: {key} item {index} begins outside reel duration")
            if "durationSec" in item and at + seconds(item["durationSec"], f"{key} duration") > cursor + 0.001:
                fail(f"{reel_id}: {key} item {index} extends beyond reel duration")
        spec[key] = value
    target.mkdir(parents=True, exist_ok=True)
    out = target / "timeline_spec.json"
    out.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return out, cursor


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plans", type=Path, required=True)
    parser.add_argument("--approvals", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    plans = json.loads(args.plans.read_text(encoding="utf-8"))
    approvals = json.loads(args.approvals.read_text(encoding="utf-8"))
    allowed = approvals.get("approved_reel_ids")
    if not isinstance(allowed, list) or not allowed or any(not isinstance(x, str) for x in allowed):
        fail("approvals.json needs a nonempty approved_reel_ids array")
    reels = plans.get("reels")
    if not isinstance(reels, list) or not reels:
        fail("plans.json needs a nonempty reels array")
    ids = [safe_id(reel.get("id")) for reel in reels]
    if len(ids) != len(set(ids)):
        fail("Duplicate reel IDs in plans")
    unapproved = set(ids) - set(allowed)
    if unapproved:
        fail(f"Unapproved reel IDs: {', '.join(sorted(unapproved))}")
    for reel in reels:
        path, duration = prepare(reel, args.output_dir.resolve())
        print(f"{reel['id']}: {duration:.3f}s -> {path}")


if __name__ == "__main__":
    main()
