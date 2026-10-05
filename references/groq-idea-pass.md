# Groq idea discovery pass

Use the user's OpenAI-compatible Groq client for **text analysis** of the ElevenLabs transcript. The model ID is `openai/gpt-oss-20b`; the base URL is `https://api.groq.com/openai/v1`. Read `GROQ_API_KEY` from the environment and keep it out of prompts and output files. Install the `openai` Python package in an isolated environment if needed when actually running this pass.

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

response = client.responses.create(
    model="openai/gpt-oss-20b",
    input=prompt_with_timestamped_transcript_chunk,
)
suggestions = response.output_text
```

Process the full episode in sequential, overlapping timestamped chunks that fit within the model context. Keep source episode ID and original timecodes on every line. Ask for candidate moments, verbatim hook excerpts, approximate in/out ranges, the payoff, missing context, and reasons to reject. Request a small number of strong candidates per chunk; accept none where the material is weak. Save raw responses under `reels-work/<episode-id>/groq/` so they can be audited.

After all chunks, merge and deduplicate suggestions by idea and source range. The agent then checks the raw word transcript and watches the promising passages. Do not copy model-produced quotes or timestamps into the user-facing ideas sheet until verified. Do not ask the model to predict virality as a probability. Its suggestions never count as user approval, and this stage creates no cut plans or timelines.

If a response fails, retry only the affected chunk a bounded number of times, then continue with direct review and note the missing model pass. If the key is absent, skip the API call and perform direct review. Never expose transcript content to Groq without the user having authorized use of this workflow for that episode.
