# The AI Brief

An agent that produces a 5–10 minute spoken brief on the most relevant and impactful AI news each weekday. It publishes the audio, chapters, show notes and sources to a private podcast page and emails you the link.

A scheduled Claude Code cloud session does each run by following [AGENT.md](AGENT.md):

1. **Research.** It searches the web for this week's AI news and cross-checks the lead stories.
2. **Write.** It writes a script meant to be heard (`episodes/<date>/script.txt`) and show notes (`notes.json`).
3. **Voice.** `make_audio.py` renders the script to MP3 with the offline Kokoro voice model and writes chapter timings.
4. **Publish.** `build_page.py` rebuilds `index.html` from every episode, then the run publishes it with the new MP3.
5. **Deliver.** It emails the takeaways and the page link.

Settings are in `config.json`.

## Running it by hand

```bash
pip install kokoro-onnx soundfile
python3 make_audio.py episodes/2026-10-29/script.txt episodes/2026-10-29/brief.mp3
python3 build_page.py
```
