# Podcast to Reels in Premiere Pro

An agent skill that reviews full podcast episodes, proposes timestamped reel ideas, waits for the creator to approve specific ideas, and then builds editable Adobe Premiere Pro timelines for reels under two minutes.

## What it does

1. Inventories and reviews each full episode.
2. Transcribes with ElevenLabs Scribe at word level and optionally runs a Groq `openai/gpt-oss-20b` idea search.
3. Presents ranked ideas with source timecodes and edit concepts. **No reel editing starts until the creator approves specific ideas.**
4. Turns approved cut plans into Premiere-compatible XML sequences and SRT captions, then finishes and verifies the edits in Premiere Pro.

Read [SKILL.md](SKILL.md) for the agent workflow and [plan-format.md](references/plan-format.md) for the approved reel plan schema.

## Requirements

- A podcast folder with source recordings; Python 3.10+ and FFmpeg/FFprobe on `PATH`.
- The [`video-use`](https://github.com/browser-use/video-use) skill for ElevenLabs transcription and inspection, or an equivalent installed source with word-level transcript support.
- The [`premiere-editing-dna`](https://github.com/vamshicreates/premiere-editing-dna) skill for Premiere timeline compilation.
- Adobe Premiere Pro for final in-app editing, saving `.prproj`, and exporting.
- `ELEVENLABS_API_KEY` for Scribe. `GROQ_API_KEY` and the `openai` Python package are needed only for the optional Groq idea pass.

The preparation script does not call either API. It checks approved IDs, media ranges, caption offsets, and the strict 120-second limit, then writes `timeline_spec.json` files for the Premiere skill's compiler.

## Installation

Install this folder as a Codex skill or place it in your agent's skills directory. Install the two dependent skills separately. The skill resolves their actual locations at runtime; it does not bundle them or configure Premiere's optional live bridge.

On Windows, use native Python and FFmpeg on `PATH`. Clone this repository into `%USERPROFILE%\.codex\skills\podcast-to-reels-premiere` (or your agent's skills directory), then install `video-use` and `premiere-editing-dna` separately. In PowerShell, use `py -3` in place of the `python3` examples. JSON media paths can use forward slashes (`C:/Videos/episode.mp4`) or escaped backslashes. Keep Premiere Pro on the same Windows host as the source media for import and finishing.

On macOS, use `python3`; install FFmpeg and the same two dependent skills. The XML/SRT compiler works without the optional Premiere CEP bridge. The bridge's setup script changes Adobe CEP settings and a Gemini MCP config, so inspect it before running it.

## Status

The plan-to-XML/SRT path has been tested with sample media on macOS. Windows uses the same Python scripts and the Premiere dependency's documented Windows path, but has not been tested end-to-end on a Windows machine. The live Premiere Pro editing/export stage requires Premiere Pro on the machine running the skill.
