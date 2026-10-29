# AI Brief agent: runbook

You produce one episode of **The AI Brief**: a 5–10 minute spoken summary of the most relevant and impactful AI news since the last episode, published as audio on a private podcast page.

## 0. Check for an existing episode

If `episodes/<today's date>/` already exists, today's episode is done. Stop without publishing or emailing.

## 1. Research (WebSearch)

Direct page fetches are blocked by this environment's network policy. Use WebSearch (`mode: "extended"`) and send searches in parallel. Cover at least:

- Overall: "AI news this week <month year>"
- Labs and models: OpenAI, Anthropic, Google DeepMind, Meta, xAI, Mistral, DeepSeek and other Chinese labs
- Money: funding rounds, IPOs, M&A, earnings that hinge on AI
- Infrastructure: chips, data centers, energy
- Safety and security: evaluations, incidents, misuse
- Policy: US federal and state, EU AI Act, UK, China
- Work and adoption: layoffs, enterprise rollouts, consumer products
- Research breakthroughs

Then run one verification search for each candidate lead story.

## 2. Select and verify

- Pick 5–7 stories by **impact**: what changes money, capability, risk or rules for many people. Ignore minor product updates.
- Prefer primary sources (company posts, SEC filings, government sites) and major outlets (Reuters, AP, Bloomberg, CNBC, FT, The Verge, TechCrunch).
- If sources conflict on a figure, say so in the script. If you cannot corroborate a story, leave it out and list it under `skipped`.
- Don't repeat stories from the previous episode unless something materially new happened. Read the last `episodes/*/notes.json` to check.

## 3. Write the script: `episodes/<YYYY-MM-DD>/script.txt`

- 1,100–1,350 words. At speed 1.1 this renders to about 8–9 minutes.
- Structure: a cold open with the date, the lead story, then one block per story, each ending with "Why this matters", then three takeaways, a one-line sourcing note, and a sign-off.
- Start each section with a `# Chapter title` line. It is not read aloud. It becomes a chapter marker.
- Write for the ear. Use short sentences and no parentheses or bullet points. Spell out numbers the way you'd say them ("sixteen point three billion dollars"). Write acronyms with dots so they're read letter by letter ("S.E.C.", "U.K."). Don't use markdown.
- Use a calm, analytical tone that is skeptical of hype and doesn't sensationalize.

## 4. Write the show notes: `episodes/<YYYY-MM-DD>/notes.json`

Use the same shape as `episodes/2026-10-29/notes.json`: `date`, `title`, `summary`, `takeaways` (3), `stories` (`tag`, `headline`, `body`, `confidence`, `sources` as `[name, url]` pairs), and `skipped`.

## 5. Render and build

```bash
python3 make_audio.py episodes/<date>/script.txt episodes/<date>/brief.mp3
python3 build_page.py
```

`make_audio.py` downloads the Kokoro voice model from GitHub on first run (about 350 MB) and writes `chapters.json`. Dependencies: `pip install kokoro-onnx soundfile`, plus `ffmpeg`.

## 6. Publish and deliver

- Publish `index.html` with the Artifact tool to the existing podcast page (`page_url` in `config.json`). In a new session, first call the Artifact tool with `action: "read"` on that URL; a publish to it is refused until you do. Then publish with `url` set to it and `file_path: index.html`. Pass `files: {"episodes/<date>/brief.mp3": "episodes/<date>/brief.mp3"}`. Earlier episodes' MP3s stay on the page.
- If `config.json` has `email`, send a short Gmail message with the episode title, the three takeaways and the page link. Don't attach the MP3; it's too large to pass inline.
- Commit and push the new episode folder to `main` (MP3s and models are gitignored). The MP3s live on the podcast page.
- If any step fails, still email a short note saying what failed, so a missed episode isn't silent.
