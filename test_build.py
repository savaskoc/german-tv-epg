"""Run with: uv run --locked python test_build.py"""
from build import EPG_URL, parse_epg, rewrite

EPG = parse_epg(b"""<tv>
  <channel id="ONE.de"><display-name>DE - ONE</display-name></channel>
  <channel id="hr.de"><display-name>DE - hr</display-name></channel>
  <channel id="WDR.de"><display-name>DE - WDR</display-name></channel>
  <channel id="zdf_neo.de"><display-name>DE - zdf_neo</display-name></channel>
  <channel id="Blank.de"><display-name></display-name></channel>
</tv>""")


def line(name, tvg_id):
    return f'#EXTINF:-1 tvg-name="{name}" tvg-id="{tvg_id}" group-title="A",{name}\nhttps://example.com\n'


result, unmatched = rewrite(
    "#EXTM3U\n"
    + line("one HD", "One.de")  # id differs only by case
    + line("hr-fernsehen", "HR.de")
    + line("WDR HD", "WDRFernsehen.de")  # by name, without HD
    + line("ZDFneo HD ", "ZDFneo.de")  # override, upstream's trailing space
    + line("Tide TV", ""),  # no match, and "" must not match the blank name
    EPG,
)
assert result == (
    f'#EXTM3U url-tvg="{EPG_URL}"\n'
    + line("one HD", "ONE.de")
    + line("hr-fernsehen", "hr.de")
    + line("WDR HD", "WDR.de")
    + line("ZDFneo HD ", "zdf_neo.de")
    + line("Tide TV", "")
), result
assert unmatched == ["Tide TV"], unmatched
print("ok")
