# german-tv-epg

Takes the [josxha/german-tv-m3u](https://github.com/josxha/german-tv-m3u) playlist, rewrites each `tvg-id` to match the [iptv-epg.org](https://iptv-epg.org/files/epg-de.xml) guide exactly, names that guide in the `url-tvg` header, and saves the result to `german-tv.m3u`. GitHub Actions checks both source URLs daily at 06:00 (05:00 UTC) and rebuilds only if either changed (hash in `.sources.sha256`); manual runs always rebuild.

Run it with `uv run --locked python build.py`, and test it with `uv run --locked python test_build.py`. The run prints the channels that have no guide data.

Channels whose guide id can't be worked out from their id or name go in `OVERRIDES` in `build.py`.
