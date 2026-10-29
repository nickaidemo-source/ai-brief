"""Build index.html (the podcast page) from every episode in episodes/.

Each episode folder holds notes.json, chapters.json, script.txt and brief.mp3.
The page embeds the notes and transcript, and references the MP3s by relative
path, so publish index.html with the MP3s as supporting files.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load_episodes():
    episodes = []
    for folder in sorted(glob.glob(os.path.join(HERE, "episodes", "*")), reverse=True):
        notes_path = os.path.join(folder, "notes.json")
        if not os.path.exists(notes_path):
            continue
        with open(notes_path, encoding="utf-8") as f:
            ep = json.load(f)
        with open(os.path.join(folder, "chapters.json"), encoding="utf-8") as f:
            ep.update(json.load(f))
        with open(os.path.join(folder, "script.txt"), encoding="utf-8") as f:
            ep["transcript"] = [p.strip() for p in f.read().split("\n\n") if p.strip() and not p.startswith("#")]
        ep["audio"] = f"episodes/{os.path.basename(folder)}/brief.mp3"
        episodes.append(ep)
    return episodes


def main():
    with open(os.path.join(HERE, "page_template.html"), encoding="utf-8") as f:
        template = f.read()
    data = json.dumps(load_episodes(), ensure_ascii=False).replace("</", "<\\/")
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(template.replace("__EPISODES__", data))
    print("wrote index.html")


if __name__ == "__main__":
    main()
