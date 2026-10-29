"""Render a podcast script to MP3 with the offline Kokoro TTS model.

Usage: python make_audio.py SCRIPT.txt OUT.mp3 [--voice am_michael] [--speed 1.1]

The script is plain text. Blank lines separate paragraphs; each paragraph is
synthesized separately and joined with a short pause, so pacing stays natural.
Lines starting with '#' are section breaks (longer pause, not read); their text
becomes a chapter title, written with start times to OUT's chapters.json.
"""
import json
import argparse
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "models", "kokoro-v1.0.onnx")
VOICES = os.path.join(HERE, "models", "voices-v1.0.bin")
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"


def ensure_models():
    os.makedirs(os.path.dirname(MODEL), exist_ok=True)
    for path in (MODEL, VOICES):
        if not os.path.exists(path):
            subprocess.run(["curl", "-sSL", "-o", path, MODEL_URL + os.path.basename(path)], check=True)


def parse(text):
    """Yield (kind, content) where kind is 'para' or 'break'."""
    para = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            if para:
                yield "para", " ".join(para)
                para = []
            yield "break", line.lstrip("# ")
        elif not line:
            if para:
                yield "para", " ".join(para)
                para = []
        else:
            para.append(line)
    if para:
        yield "para", " ".join(para)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("out")
    ap.add_argument("--voice", default="am_michael")
    ap.add_argument("--speed", type=float, default=1.1)
    args = ap.parse_args()

    ensure_models()
    kokoro = Kokoro(MODEL, VOICES)
    with open(args.script, encoding="utf-8") as f:
        items = list(parse(f.read()))

    chunks, sr, chapters = [], 24000, [{"title": "Intro", "start": 0.0}]
    for kind, content in items:
        if kind == "break":
            chunks.append(np.zeros(int(sr * 1.2), dtype=np.float32))
            start = sum(len(c) for c in chunks) / sr
            chapters.append({"title": content, "start": round(start, 1)})
            continue
        samples, sr = kokoro.create(content, voice=args.voice, speed=args.speed, lang="en-us")
        chunks.append(samples.astype(np.float32))
        chunks.append(np.zeros(int(sr * 0.5), dtype=np.float32))

    audio = np.concatenate(chunks)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio, sr)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name, "-codec:a", "libmp3lame", "-b:a", "96k", args.out],
            check=True,
        )
    os.unlink(tmp.name)
    meta = {"duration": round(len(audio) / sr, 1), "chapters": chapters}
    with open(os.path.join(os.path.dirname(os.path.abspath(args.out)), "chapters.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(f"{args.out}: {len(audio) / sr / 60:.1f} min")


if __name__ == "__main__":
    sys.exit(main())
