import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor

data_dir = sys.argv[1]
rows = json.load(open(os.path.join(data_dir, "responses.json")))
os.makedirs(os.path.join(data_dir, "batches"), exist_ok=True)

PROMPT = """Below are social media responses to the prompt "Gun to your head, name a song that's over 6 minutes long."

For each response, extract every specific song the person is nominating. Normalize each to the canonical
"Artist - Song Title" form, using standard capitalization and the most common official title
(e.g. "Lynyrd Skynyrd - Free Bird", "Led Zeppelin - Stairway to Heaven", "Weird Al Yankovic - Albuquerque").
Infer the artist when only a well-known title is given and it is unambiguous. If the artist cannot be
determined, use "Unknown - Title". The link_title field (title of an attached link, e.g. a YouTube video) is
a strong hint. Ignore jokes that don't name a song, whole albums, whole discographies, and songs the person
is explicitly rejecting. A quote of the original prompt with only a link still counts if the link names a song.

Return ONLY a JSON object mapping each id (as a string) to a list of song strings (empty list if none).
No prose, no code fences.

RESPONSES:
"""


def run(batch_idx, batch):
    out = os.path.join(data_dir, "batches", f"{batch_idx:03d}.json")
    if os.path.exists(out):
        return
    lines = [json.dumps({"id": i, "text": r["text"], "link_title": r["link_title"]}, ensure_ascii=False)
             for i, r in batch]
    prompt = PROMPT + "\n".join(lines)
    for attempt in range(3):
        p = subprocess.run(["claude", "-p", "--model", "sonnet", "--output-format", "text"],
                           input=prompt, capture_output=True, text=True)
        txt = p.stdout.strip()
        if txt.startswith("```"):
            txt = txt.split("\n", 1)[1].rsplit("```", 1)[0]
        try:
            parsed = json.loads(txt)
            json.dump(parsed, open(out, "w"), ensure_ascii=False)
            print("done", batch_idx, file=sys.stderr)
            return
        except Exception:
            print("bad output", batch_idx, attempt, p.stderr[:200], txt[:200], file=sys.stderr)


indexed = list(enumerate(rows))
size = 200
batches = [indexed[i:i + size] for i in range(0, len(indexed), size)]
with ThreadPoolExecutor(8) as ex:
    list(ex.map(lambda a: run(*a), enumerate(batches)))
