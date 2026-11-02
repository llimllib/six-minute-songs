# /// script
# dependencies = ["matplotlib"]
# ///
import json, sys
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ranked = json.load(open(sys.argv[1]))
out = sys.argv[2]
N = 40

top = ranked[:N][::-1]
labels = [r["song"].replace(" - ", " — ", 1) for r in top]
votes = [r["votes"] for r in top]

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(18, 14), gridspec_kw={"width_ratios": [3, 2]})
bars = ax.barh(labels, votes, color="#1185fe")
ax.bar_label(bars, padding=3, fontsize=9)
ax.set_title(f"Top {N} songs", fontsize=14, loc="left")
ax.set_xlabel("People naming it")
ax.tick_params(axis="y", labelsize=9.5)
ax.margins(y=0.01)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# artists, summing votes across all of their songs
artists = Counter()
for r in ranked:
    artists[r["song"].split(" - ", 1)[0]] += r["votes"]
artists.pop("Unknown", None)
atop = artists.most_common(25)[::-1]
abars = ax2.barh([a for a, _ in atop], [v for _, v in atop], color="#f2a03d")
ax2.bar_label(abars, padding=3, fontsize=9)
ax2.set_title("Top 25 artists (all songs combined)", fontsize=14, loc="left")
ax2.set_xlabel("Votes")
ax2.margins(y=0.01)
for s in ("top", "right"):
    ax2.spines[s].set_visible(False)

fig.suptitle("“Gun to your head, name a song that’s over 6 minutes long.”\n"
             "Bluesky responses to @concretexros3 — 1,540 replies + 3,457 quote posts; "
             f"{len(ranked):,} distinct songs; one vote per person per song",
             fontsize=15, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(out, dpi=130)
