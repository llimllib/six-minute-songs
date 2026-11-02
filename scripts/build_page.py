"""Render data/ranked.json into a single static HTML page.

usage: python3 scripts/build_page.py data/ranked.json data/responses.json site/index.html
"""
import json, os, sys
from collections import Counter, defaultdict
from html import escape

ranked = json.load(open(sys.argv[1]))
responses = json.load(open(sys.argv[2]))
out = sys.argv[3]

POST_URL = "https://bsky.app/profile/concretexros3.bsky.social/post/3mzbzudooyc2y"
N_SONGS = 50
N_ARTISTS = 20


def split(song):
    artist, _, title = song.partition(" - ")
    return artist, title


kinds = Counter(r["kind"] for r in responses)
total_votes = sum(r["votes"] for r in ranked)
singletons = sum(1 for r in ranked if r["votes"] == 1)

artist_votes = Counter()
artist_songs = defaultdict(int)
for r in ranked:
    a, _ = split(r["song"])
    if a == "Unknown":
        continue
    artist_votes[a] += r["votes"]
    artist_songs[a] += 1


def bar_rows(items, max_value, cls=""):
    rows = []
    for i, (label, sub, value) in enumerate(items, 1):
        frac = value / max_value
        rows.append(f"""
      <div class="row{' ' + cls if cls else ''}">
        <div class="rank">{i}</div>
        <div class="label"><span class="title">{escape(label)}</span> <span class="sub">{escape(sub)}</span></div>
        <div class="bar-cell"><div class="bar" style="width:calc((100% - 36px) * {frac:.4f})"></div><span class="value">{value}</span></div>
      </div>""")
    return "".join(rows)


song_items = [(split(r["song"])[1], split(r["song"])[0], r["votes"]) for r in ranked[:N_SONGS]]
artist_items = [(a, f"{artist_songs[a]} songs" if artist_songs[a] != 1 else "1 song", v)
                for a, v in artist_votes.most_common(N_ARTISTS)]

all_songs = [[*split(r["song"]), r["votes"]] for r in ranked]

top = ranked[0]
top_artist, top_title = split(top["song"])
rush_songs = artist_songs["Rush"]

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Name a Song Over Six Minutes Long</title>
<meta name="description" content="{len(responses):,} Bluesky users were asked to name a song over six minutes long. Here is what they picked.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #121212;
    --muted: #727272;
    --rule: #e2e2e2;
    --bar: #d98c3f;
    --bar-alt: #5b8fa8;
    --sans: "Libre Franklin", "Helvetica Neue", Arial, sans-serif;
    --serif: "Source Serif 4", Georgia, "Times New Roman", serif;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; color: var(--ink); background: #fff; font-family: var(--serif); }}
  header.mast {{ border-bottom: 1px solid var(--ink); padding: 10px 20px; font-family: var(--sans);
    font-weight: 800; font-size: 13px; letter-spacing: .02em; }}
  header.mast a {{ color: inherit; text-decoration: none; }}
  main {{ padding: 0 20px 80px; }}
  .col {{ max-width: 600px; margin: 0 auto; }}
  .wide {{ max-width: 720px; margin: 0 auto; }}
  .kicker {{ font-family: var(--sans); font-size: 13px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .06em; margin: 48px 0 10px; }}
  h1 {{ font-family: var(--serif); font-weight: 700; font-size: clamp(30px, 5vw, 44px); line-height: 1.12;
    margin: 0 0 14px; letter-spacing: -.01em; }}
  .dek {{ font-size: 20px; line-height: 1.4; color: #333; margin: 0 0 18px; }}
  .byline {{ font-family: var(--sans); font-size: 13px; color: var(--muted); margin-bottom: 36px; }}
  p {{ font-size: 19px; line-height: 1.55; margin: 0 0 1.1em; }}
  p a, .notes a {{ color: inherit; text-decoration-color: #aaa; text-underline-offset: 2px; }}
  h2 {{ font-family: var(--sans); font-size: 17px; font-weight: 700; margin: 44px 0 4px; }}
  .chart-note {{ font-family: var(--sans); font-size: 13px; color: var(--muted); margin: 0 0 14px; }}

  .chart {{ font-family: var(--sans); font-size: 14px; border-top: 1px solid var(--ink); margin-bottom: 36px; }}
  .row {{ display: grid; grid-template-columns: 26px minmax(0, 1fr) minmax(0, 1fr); align-items: center;
    gap: 10px; padding: 5px 0; border-bottom: 1px solid var(--rule); }}
  .rank {{ color: var(--muted); font-size: 12px; text-align: right; font-variant-numeric: tabular-nums; }}
  .label {{ line-height: 1.25; }}
  .title {{ font-weight: 500; }}
  .sub {{ color: var(--muted); font-size: 13px; }}
  .bar-cell {{ display: flex; align-items: center; gap: 6px; }}
  .bar {{ height: 14px; background: var(--bar); flex: none; }}
  .alt .bar {{ background: var(--bar-alt); }}
  .value {{ font-size: 12px; font-variant-numeric: tabular-nums; color: #333; }}
  .row:nth-child(-n+10 of .row:not(.alt)) .title {{ font-weight: 700; }}

  .search {{ font-family: var(--sans); margin: 8px 0 40px; }}
  .search input {{ width: 100%; font: inherit; font-size: 16px; padding: 9px 10px; border: 1px solid #999;
    border-radius: 0; }}
  .search input:focus {{ outline: 2px solid var(--ink); outline-offset: -1px; }}
  .search table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
  .search th {{ text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .05em;
    color: var(--muted); font-weight: 500; border-bottom: 1px solid var(--ink); padding: 6px 4px; }}
  .search td {{ border-bottom: 1px solid var(--rule); padding: 6px 4px; }}
  .search td.n, .search th.n {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .search .count {{ font-size: 12px; color: var(--muted); margin-top: 8px; }}

  .notes {{ font-family: var(--sans); font-size: 13px; line-height: 1.55; color: #444;
    border-top: 1px solid var(--rule); padding-top: 14px; margin-top: 40px; }}
  .notes p {{ font-size: 13px; line-height: 1.55; }}

  @media (max-width: 560px) {{
    .row {{ grid-template-columns: 22px minmax(0, 1fr) 90px; }}
    p {{ font-size: 17px; }}
    .dek {{ font-size: 18px; }}
  }}
</style>
</head>
<body>
<header class="mast"><a href="{POST_URL}">Six Minutes or More</a></header>
<main>
  <div class="col">
    <div class="kicker">Bluesky, Nov. 2, 2026</div>
    <h1>Gun to Your Head, Name a Song Over Six Minutes Long. Bluesky Said ‘{escape(top_title)}.’</h1>
    <p class="dek">We read {len(responses):,} replies and quote posts and counted every song people named.
      There were {len(ranked):,} different answers.</p>
    <div class="byline">Data collected Nov. 2, 2026</div>

    <p>The <a href="{POST_URL}">prompt</a> was simple and the answers were not. People named a single song,
      or five of them, or explained why one song couldn’t possibly be enough. Sorting through them all turned
      up {total_votes:,} picks.</p>
    <p>{escape(top_artist)}’s 17-minute “{escape(top_title)}” finished first by a wide margin, named by
      {top["votes"]} people, about half again as many as the runner-up, Don McLean’s “American Pie.” Most of the songs on the leaderboard come from the classic rock and progressive rock of the
      1960s and ’70s, with a few exceptions: Weird Al’s “Albuquerque” came in third, and Taylor Swift,
      Frank Ocean and Green Day all made the top 40.</p>
  </div>

  <div class="wide">
    <h2>The {N_SONGS} most-named songs</h2>
    <p class="chart-note">Number of people who named each song</p>
    <div class="chart">{bar_rows(song_items, song_items[0][2])}
    </div>
  </div>

  <div class="col">
    <p>Counting by artist changes the order. “2112” was Rush’s only song in the top 10, but people named
      {rush_songs} different Rush songs, from “Xanadu” to “La Villa Strangiato,” and together they add up
      to more mentions than any other band got. Pink Floyd’s best-placed song came in 21st, yet the band
      finished fourth among artists. Iron Butterfly is second on the strength of a single song.</p>
  </div>

  <div class="wide">
    <h2>The {N_ARTISTS} most-named artists</h2>
    <p class="chart-note">Total mentions across all of an artist’s songs</p>
    <div class="chart">{bar_rows(artist_items, artist_items[0][2], "alt")}
    </div>
  </div>

  <div class="col">
    <p>Past the leaderboard, the list gets long. {singletons:,} songs, about
      {round(100 * singletons / len(ranked))} percent of the total, were named by exactly one person. The top
      10 songs account for only {round(100 * sum(r["votes"] for r in ranked[:10]) / total_votes)} percent of
      all picks.</p>
    <p>Not everyone followed the rules. “Bohemian Rhapsody,” which runs five minutes and 55 seconds,
      got {next((r["votes"] for r in ranked if r["song"].endswith("Bohemian Rhapsody")), 0)} votes anyway.
      John Cage’s “4′33″” got
      {next((r["votes"] for r in ranked if "4'33" in r["song"]), 0)}.</p>

    <h2>Search every song</h2>
    <p class="chart-note">All {len(ranked):,} songs, by title or artist</p>
    <div class="search">
      <input id="q" type="search" placeholder="Try “Dylan” or “Rapper’s Delight”" autocomplete="off">
      <table>
        <thead><tr><th class="n">#</th><th>Song</th><th>Artist</th><th class="n">Votes</th></tr></thead>
        <tbody id="results"></tbody>
      </table>
      <div class="count" id="count"></div>
    </div>

    <div class="notes">
      <p><strong>About the data.</strong> Responses are all {kinds["reply"]:,} replies and {kinds["quote"]:,}
        quote posts to <a href="{POST_URL}">the original post</a> as of Nov. 2, 2026. A language model pulled
        song names out of each post, including the titles of attached YouTube and Spotify links, and put them
        in a standard “artist, title” form. Jokes, whole albums and “everything by this band” answers were not
        counted. Each person counts once per song, even if they both replied and quoted. Covers by a different
        artist are counted separately. Automated extraction makes mistakes, mostly among songs with only a
        vote or two.</p>
      <p>Code and data: <a href="https://github.com/llimllib/six-minute-songs">github.com/llimllib/six-minute-songs</a></p>
    </div>
  </div>
</main>
<script>
const SONGS = {json.dumps(all_songs, ensure_ascii=False, separators=(",", ":"))};
const q = document.getElementById("q");
const tbody = document.getElementById("results");
const count = document.getElementById("count");
const fold = s => s.normalize("NFKD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase();
const indexed = SONGS.map((s, i) => [i + 1, s, fold(s[0] + " " + s[1])]);

function render() {{
  const terms = fold(q.value).split(/\\s+/).filter(Boolean);
  const hits = terms.length ? indexed.filter(([, , t]) => terms.every(w => t.includes(w))) : indexed;
  const shown = hits.slice(0, 25);
  tbody.replaceChildren(...shown.map(([rank, [artist, title, votes]]) => {{
    const tr = document.createElement("tr");
    for (const [v, cls] of [[rank, "n"], [title, ""], [artist, ""], [votes, "n"]]) {{
      const td = document.createElement("td");
      td.textContent = v;
      if (cls) td.className = cls;
      tr.append(td);
    }}
    return tr;
  }}));
  count.textContent = hits.length > shown.length
    ? `Showing ${{shown.length}} of ${{hits.length.toLocaleString()}} songs`
    : `${{hits.length.toLocaleString()}} song${{hits.length === 1 ? "" : "s"}}`;
}}
q.addEventListener("input", render);
render();
</script>
</body>
</html>
"""

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
open(out, "w").write(html)
