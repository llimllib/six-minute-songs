# six-minute-songs

What Bluesky picked when [@concretexros3](https://bsky.app/profile/concretexros3.bsky.social/post/3mzbzudooyc2y)
asked: "Gun to your head, name a song that's over 6 minutes long."

Page: https://llimllib.github.io/six-minute-songs/

## Data

- `data/responses.json`: every reply and quote post (text, author handle, attached link title), collected Nov. 2, 2026
- `data/batches/`: songs extracted from each post, keyed by index into `responses.json`
- `data/ranked.json`: songs ranked by number of distinct people naming them
- `songs.csv`: the same ranking as CSV
- `chart.png`: top 40 songs and top 25 artists

## Pipeline

```sh
# 1. fetch replies (via the Constellation backlink index) and quote posts
python3 scripts/fetch.py data

# 2. extract songs with `claude -p`, 200 posts per batch; skips batches that already exist
python3 scripts/extract.py data

# 3. merge spelling variants and count one vote per person per song
python3 scripts/aggregate.py data scripts/aliases.json

# 4. outputs
uv run scripts/chart.py data/ranked.json chart.png
python3 scripts/build_page.py data/ranked.json data/responses.json site/index.html
```

Step 2 needs the [Claude Code](https://claude.com/claude-code) CLI. The other steps use
only public, unauthenticated APIs. `scripts/aliases.json` holds hand-made merges for
variants the extractor named inconsistently.

The GitHub Action in `.github/workflows/pages.yml` runs step 4's page build and publishes `site/` to GitHub Pages.
