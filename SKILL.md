---
name: podcast-to-reels-premiere
description: Analyze complete podcast recordings, propose timestamped short-form reel ideas for approval, then build approved reels as editable Adobe Premiere Pro timelines with captions and verified exports.
---

# Podcast to Reels in Premiere Pro

Turn full podcast episodes in a user-provided folder into strong standalone reels. The user approves **specific ideas before any reel editing**. Every finished reel must be shorter than 120 seconds. Do not describe a clip as guaranteed to go viral.

## Dependencies and scope

- Locate the installed `video-use` skill through the active skills catalog or workspace. Use it for source inspection, ElevenLabs Scribe word-level transcription, transcript packing, and visual/audio checks. Its FFmpeg renderer is not the reel editor for this workflow.
- Locate the installed `premiere-editing-dna` skill through the active skills catalog. Use it for editable Premiere timeline compilation and, when available, live Premiere inspection. Resolve its actual path before invoking scripts. Its silence auto-cut and preset zoom cadence are optional; make editorial cuts from the approved idea and transcript instead.
- The podcast footage and all generated work stay inside the user-specified podcast folder. Never alter source media. Use a `reels-work/` subfolder for analysis, plans, Premiere XML/SRT, previews, and exports.
- ElevenLabs transcription uploads audio to the provider and may incur usage. Use it when the user has requested this workflow and an API key is configured; never print or copy the key into project files. If unavailable, report the blocker and use a suitable local transcription engine only if it preserves the timing needed for clip decisions.
- Use Groq's `openai/gpt-oss-20b` through the OpenAI-compatible Responses API for a first-pass search of reel ideas when `GROQ_API_KEY` and the `openai` Python package are available. Follow [the Groq idea pass](references/groq-idea-pass.md). This is text analysis after transcription; it does not replace ElevenLabs Scribe. Treat model suggestions as leads to verify, not editorial decisions.
- Do not run the Premiere skill's setup script automatically. It changes Adobe CEP settings, installs a local extension, and updates a Gemini MCP config. Use its XML compiler without that setup; configure the live bridge only if needed for an authorized Premiere session.

## Phase 1 — Inventory every complete episode

1. Identify every intended full podcast file in the input folder. Distinguish episodes from trailers, teasers, alternate exports, and camera angles using file metadata and the user's folder organization. If identity is ambiguous, make a best-effort inventory and ask only about the unresolved files.
2. Record path, duration, frame size, frame rate, audio streams, language if known, and a stable source fingerprint (path + size + modification time, or a content hash). Give each episode its own `reels-work/<episode-id>/` directory to avoid same-basename transcript collisions.
3. Inspect the full episode, including the opening and ending. Do not shortlist from a teaser, excerpt, or a partial transcript while claiming full-episode coverage. Note camera setup, speaker changes, reactions, on-screen material, and audio issues.

## Phase 2 — Transcribe and understand

1. Transcribe **the entire episode** with ElevenLabs Scribe using word-level verbatim timestamps, speaker diarization, and audio-event tags. The local `video-use/helpers/transcribe.py` can write the raw JSON. If the episode has multiple audio tracks, identify the dialogue track before upload.
2. Cache the transcript against the source fingerprint. The `video-use` helper skips an existing filename without checking whether the source changed; remove or replace a stale cache deliberately when the fingerprint differs.
3. Pack the transcript into timestamped phrases for reading, but retain the raw word JSON for cut points and captions. Check names, code-switching, technical terms, low-confidence phrases, speaker attribution, and quoted claims against the recording.
4. Read the transcript from start to finish. Build a topic map with time ranges and note stories, surprising answers, strong opinions, practical lessons, humor, emotion, disagreement, and revealing reactions. Inspect the source video at each promising passage; transcript appeal alone is insufficient.
5. If Groq is configured, run the first-pass idea search on timestamped transcript chunks covering the **entire** episode. Save its raw suggestions separately and independently verify every proposed quote, timestamp, context, and payoff against the transcript and source recording. If Groq is unavailable, do the same discovery pass directly; do not leave any episode unreviewed.

## Phase 3 — Propose ideas only

Find a broad set of distinct candidates, then rank them. Favor a hook that works in the first seconds, one coherent point or story, a clear payoff, understandable context, credible claims, clean audio, and useful visual/reaction material. Avoid duplicate angles, misleading rearrangement, and punchlines whose setup cannot fit. Preserve the speaker's meaning. A continuous excerpt is preferable when it works; a noncontiguous cut is acceptable when transitions remain truthful and natural.

For each candidate, give the user an idea card with:

- Stable ID and working title; episode and exact source time range(s).
- Verbatim hook line, one-sentence premise, key payoff, and estimated finished duration **below 120 seconds**.
- Why the audience might watch or share it, plus any context or accuracy caveat.
- Proposed edit shape: opening, essential beats, ending, useful reaction/B-roll/caption treatment.
- Priority (high/medium/experimental) and a brief reason. Treat this as editorial judgment, not a numerical viral prediction.

Put the ranked cards in `reels-work/ideas.md` and structured data in `reels-work/ideas.json`. Show the ideas to the user and **stop at this gate**. Transcript generation, source review, and idea cards are analysis; do not create reel cut plans, Premiere timelines, previews, or exports yet. The user may approve, reject, combine, or revise cards. Record only explicit approvals in `reels-work/approvals.json`; do not interpret silence as approval.

## Phase 4 — Plan approved reels

For each approved ID, select exact word-boundary source in/out points, with enough padding to avoid clipped consonants and breaths. Decide whether the reel needs a cold-open, a question, a reaction, or a brief context bridge. Keep total planned duration below 120 seconds, including any intro or outro. If an approved idea cannot make a truthful, watchable reel within that limit, explain the issue and seek a revised idea before editing it.

Write a clip plan using [the plan format](references/plan-format.md). Captions use verbatim transcript text and source timestamps, then map to output time after cuts. Use `scripts/prepare_premiere.py` with the recorded approval IDs to validate source ranges, runtime, and output caption timing and to emit one Premiere `timeline_spec.json` per approved reel. The helper deliberately refuses unapproved IDs and durations of 120 seconds or more.

## Phase 5 — Build and finish in Premiere Pro

1. Use this skill's `scripts/compile_premiere.py --spec <timeline_spec.json> --builder <path-to-premiere-editing-dna/scripts/build_premiere_sequence.py>` to compile each editable XML timeline and SRT. Import the XML and SRT into Premiere Pro. The wrapper avoids a CLI parsing bug in some versions of the Premiere dependency. If a working live bridge is available, it may assist; verify the resulting sequence in Premiere rather than assuming the bridge succeeded.
2. Finish the edit in Premiere Pro: vertical 9:16 framing unless the user specifies another target, deliberate cuts, clean dialogue, readable captions within safe areas, color consistency, and only justified B-roll, graphics, music, or SFX. Do not apply a default zoom, ducking level, or visual style merely because the source skill has one. Use approved edits as style reference when supplied.
3. Save the editable Premiere project alongside the reel's XML and SRT. Export the reel from Premiere Pro. If Premiere is unavailable, stop at the validated editable XML/SRT and report that in-app finish/export is pending; do not present an FFmpeg render as a Premiere export.

## Phase 6 — Review and deliver

Watch every exported reel end to end. Check the first seconds, factual continuity, speaker and lip sync, audio cuts, caption spelling/timing, safe-area framing, last beat, black frames, and export duration (<120 seconds). Compare the finished result with the approved idea. Fix defects in Premiere and re-export. Deliver the reel files, editable Premiere project, XML/SRT, and a short per-reel note with source timecodes. Keep source media untouched and preserve transcript/idea/approval records so future edits can reuse them.

If a tool, API key, source file, or Premiere installation is missing, complete all independent analysis or preparation that remains possible, then name the exact blocked stage and required input. Never claim an unverified timeline or export was completed.
