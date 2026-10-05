# Approved reel plan format

Save a JSON object with a `reels` array. Every reel ID must occur in `approvals.json` under `approved_reel_ids` before `prepare_premiere.py` will compile it. The plan is made only after that approval.

```json
{
  "reels": [
    {
      "id": "episode-01-reel-03",
      "title": "A decision that changed the film",
      "fps": 30,
      "width": 1080,
      "height": 1920,
      "segments": [
        {
          "path": "/absolute/path/to/full-episode.mp4",
          "inSec": 245.2,
          "outSec": 259.8,
          "captions": [
            {"startSec": 245.3, "endSec": 247.1, "text": "I almost walked away."}
          ]
        }
      ],
      "v2_broll": [],
      "v3_overlays": [],
      "a2_sfx": [],
      "a3_bgm": [],
      "markers": [{"name": "HOOK", "timeSec": 0, "comment": "Opening line"}]
    }
  ]
}
```

`inSec` and `outSec` are source-media seconds. Caption times inside a segment are also source-media seconds. Segment order is the intended output order; gaps between source segments are removed. The helper maps captions to the output timeline and generates a `v1_aroll` Premiere timeline specification. Optional V2/V3/A2/A3 items use the field names and **output-timeline** seconds from the installed `premiere-editing-dna` builder. The helper passes them through; inspect their paths, overlaps, and duration in Premiere.

`approvals.json` example:

```json
{"approved_reel_ids": ["episode-01-reel-03"]}
```

Run:

```bash
python3 scripts/prepare_premiere.py \
  --plans /path/to/reels-work/plans.json \
  --approvals /path/to/reels-work/approvals.json \
  --output-dir /path/to/reels-work/premiere-specs
```

Then compile each emitted spec with the installed Premiere skill's `build_premiere_sequence.py build <spec-path>`. Import the generated XML and SRT into Premiere Pro. The XML is an editable interchange sequence; it becomes a `.prproj` only when saved from Premiere Pro.
