import json, os, re, sys, unicodedata
from collections import Counter, defaultdict

data_dir = sys.argv[1]
rows = json.load(open(os.path.join(data_dir, "responses.json")))
picks = {}
for f in sorted(os.listdir(os.path.join(data_dir, "batches"))):
    picks.update({int(k): v for k, v in json.load(open(os.path.join(data_dir, "batches", f))).items()})

# manual merges for variants the extractor produced inconsistently
ALIASES = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}


def key(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", "and")
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)
    s = re.sub(r"\bthe\b|\bpts?\b|\bparts?\b", "", s)
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


def title_key(s):
    return key(s.split(" - ", 1)[1]) if " - " in s else key(s)


# collapse "Unknown - X" into the known artist with the most votes for the same title
by_title = defaultdict(Counter)
for songs in picks.values():
    for s in songs:
        if not s.startswith("Unknown - "):
            by_title[title_key(s)][s] += 1

votes = defaultdict(set)  # canonical key -> set of authors
display = defaultdict(Counter)
for i, songs in picks.items():
    author = rows[i]["author"]
    for s in songs:
        s = ALIASES.get(s, s)
        if s.startswith("Unknown - ") and by_title.get(title_key(s)):
            s = by_title[title_key(s)].most_common(1)[0][0]
        k = key(s)
        k = ALIASES.get(k, k)
        votes[k].add(author)
        display[k][s] += 1

ranked = sorted(votes, key=lambda k: -len(votes[k]))
result = [{"song": display[k].most_common(1)[0][0], "votes": len(votes[k]),
           "variants": dict(display[k])} for k in ranked]
json.dump(result, open(os.path.join(data_dir, "ranked.json"), "w"), indent=1, ensure_ascii=False)

n_posts = sum(1 for v in picks.values() if v)
print(f"posts with a song: {n_posts} / {len(rows)}; unique songs: {len(result)}; "
      f"unique voters: {len({rows[i]['author'] for i, v in picks.items() if v})}")
for r in result[:int(sys.argv[3]) if len(sys.argv) > 3 else 120]:
    print(r["votes"], r["song"], "" if len(r["variants"]) == 1 else list(r["variants"])[:6])
