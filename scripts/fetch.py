"""Fetch every reply and quote post of the original post into data/responses.json.

The public thread API only returns ~200 replies, so reply URIs come from the
Constellation backlink index and are then hydrated with getPosts.
"""
import json, os, sys, time, urllib.request, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_common import simplify

URI = "at://did:plc:bdcmqgbi2u3hauyujqy5owtr/app.bsky.feed.post/3mzbzudooyc2y"
API = "https://public.api.bsky.app/xrpc/"
CONSTELLATION = "https://constellation.microcosm.blue/links"
out_dir = sys.argv[1] if len(sys.argv) > 1 else "data"


def get(url):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print("retry", e, file=sys.stderr)
            time.sleep(2 ** attempt)
    raise RuntimeError(url)


# replies
uris = []
cursor = None
while True:
    params = {"target": URI, "collection": "app.bsky.feed.post",
              "path": ".reply.parent.uri", "limit": 100}
    if cursor:
        params["cursor"] = cursor
    d = get(CONSTELLATION + "?" + urllib.parse.urlencode(params))
    for r in d["linking_records"]:
        uris.append(f"at://{r['did']}/{r['collection']}/{r['rkey']}")
    cursor = d.get("cursor")
    if not cursor or not d["linking_records"]:
        break

rows = []
for i in range(0, len(uris), 25):
    q = urllib.parse.urlencode([("uris", u) for u in uris[i:i + 25]])
    d = get(API + "app.bsky.feed.getPosts?" + q)
    rows.extend(simplify(p, "reply") for p in d["posts"])
print("replies", len(rows), file=sys.stderr)

# quotes
cursor = None
nq = 0
while True:
    params = {"uri": URI, "limit": 100}
    if cursor:
        params["cursor"] = cursor
    d = get(API + "app.bsky.feed.getQuotes?" + urllib.parse.urlencode(params))
    for p in d.get("posts", []):
        rows.append(simplify(p, "quote"))
        nq += 1
    cursor = d.get("cursor")
    if not cursor or not d.get("posts"):
        break
print("quotes", nq, file=sys.stderr)

json.dump(rows, open(os.path.join(out_dir, "responses.json"), "w"), indent=1)
