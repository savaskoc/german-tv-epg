"""Rewrite the german-tv-m3u playlist so its tvg-ids match the iptv-epg.org guide."""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request, urlopen

PLAYLIST_URL = "https://raw.githubusercontent.com/josxha/german-tv-m3u/main/german-tv.m3u"
EPG_URL = "https://iptv-epg.org/files/epg-de.xml"

# Channels whose guide id can't be derived from their tvg-id or name.
OVERRIDES = {
    "ZDFneo": "zdf_neo.de",
    "NDR Niedersachsen": "NDRFernsehenNiedersachsen.de",
    "SWR Baden-Württemberg": "SWRBW.de",
}


def fetch(url):
    return urlopen(Request(url, headers={"User-Agent": "german-tv-epg"}), timeout=120).read()


def parse_epg(xml):
    """Guide ids, keyed by lowercased id and by lowercased display name."""
    epg = {}
    for channel in ET.fromstring(xml).iter("channel"):
        id_ = channel.get("id")
        epg[id_.lower()] = id_
        epg.setdefault(channel.findtext("display-name", "").removeprefix("DE - ").strip().lower(), id_)
    return epg


def match_id(epg, tvg_id, name):
    """The id as the guide spells it. Players compare ids exactly, case included."""
    name = name.strip()
    plain = name.removesuffix(" HD")
    keys = (OVERRIDES.get(plain), tvg_id, name, plain)
    return next((epg[key.lower()] for key in keys if key and key.lower() in epg), None)


def rewrite(playlist, epg):
    """Returns the new playlist and the names of channels with no guide data."""
    unmatched = []

    def fix(line):
        matched = match_id(epg, line[2], line[1])
        if not matched:
            unmatched.append(line[1].strip())
        return f'tvg-name="{line[1]}" tvg-id="{matched or line[2]}"'

    # ponytail: assumes tvg-name comes right before tvg-id, as upstream writes it.
    # main() fails the run if that ever changes.
    result = re.sub(r'tvg-name="([^"]*)" tvg-id="([^"]*)"', fix, playlist)
    return re.sub(r"^#EXTM3U.*", f'#EXTM3U url-tvg="{EPG_URL}"', result, count=1), unmatched


def main():
    result, unmatched = rewrite(fetch(PLAYLIST_URL).decode(), parse_epg(fetch(EPG_URL)))
    channels = result.count("#EXTINF")
    # A bad download must fail the run, not replace a good playlist.
    if not channels or channels == len(unmatched) or channels != result.count("tvg-name="):
        sys.exit(f"refusing to write: {channels} channels, {len(unmatched)} unmatched")
    Path("german-tv.m3u").write_text(result, encoding="utf-8")
    print(f"{channels - len(unmatched)} of {channels} matched. No guide data:", ", ".join(unmatched))


if __name__ == "__main__":
    main()
