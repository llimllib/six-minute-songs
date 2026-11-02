def simplify(post, kind):
    rec = post["record"]
    text = rec.get("text", "")
    # pull link card titles too; people often post youtube/spotify links
    embed = post.get("embed") or {}
    ext = embed.get("external") or (embed.get("media") or {}).get("external")
    return {
        "kind": kind,
        "uri": post["uri"],
        "author": post["author"]["handle"],
        "text": text,
        "link_title": ext.get("title") if ext else None,
        "link_uri": ext.get("uri") if ext else None,
        "likes": post.get("likeCount", 0),
    }


