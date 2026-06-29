# ZUL-IPTV

A hand-curated IPTV playlist (`ZUL-IPTV.m3u`) for use on Samsung TV (and any
M3U-compatible player) from the Jakarta / Bekasi area. **Every channel is
verified to actually decode video** (not just return an HTTP 200), so you should
not get the "logo only, no picture" problem.

## How to use on a Samsung TV

1. Use the **raw** URL of `ZUL-IPTV.m3u` from this repo, e.g.
   `https://raw.githubusercontent.com/zulfikar2701/zul-iptv-playlist/main/ZUL-IPTV.m3u`
2. Open an M3U player app on the TV (e.g. **IPTV Smarters**, **OTT Navigator**,
   **Tivimate**) and import the URL. You can also copy `ZUL-IPTV.m3u` to a USB
   stick and open it directly.

## Curation criteria

Channels were selected from the [iptv-org](https://github.com/iptv-org/iptv)
public lists (Indonesian, Sports, Movies) according to:

1. **Actually plays from Indonesia / Jakarta / Bekasi** – every stream is opened
   with ffmpeg from a Bekasi connection and must decode real video frames. Dead
   or geo-blocked streams (that show only a logo) are excluded.
2. **Popular** – well-known national / international channels.
3. **High quality content** – film channels that air recent / popular titles
   rather than random B-movies.
4. **World Cup 2026** – includes likely broadcasters / official channels
   (FIFA+, beIN Sports, SPOTV, Star Sports, Alkass).
5. **Under 50 channels total.**

## Groups

- **Indonesia** – Nusantara TV, TVRI (national + Jakarta), RRI Net, Magna
  Channel, ROCK Action, Nickelodeon Asia, Indonesiana.TV, Jawa Pos TV, etc.
- **Sports - World Cup 2026** – FIFA+ (several languages), beIN Sports USA /
  XTRA, SPOTV / SPOTV 2, Star Sports 1 HD, Alkass One.
- **Sports** – Real Madrid TV, Sportitalia, SuperTennis, Win Sports, NHL
  Network, Red Bull TV, Polsat Sport.
- **Movies** – AMC, IFC, SYFY, Paramount Network, AXN, Starz Cinema, Lifetime
  Movies, Rakuten Top/Action/Comedy/Drama Movies UK, MovieSphere, Runtime, the
  Pluto TV movie channels, Gravitas Movies.

## Testing mechanism (`test_playlist.py`)

IPTV streams are community-maintained and go offline without notice. Use the
included tester to re-verify the playlist at any time. It **decodes video with
ffmpeg** (honouring each channel's user-agent / referrer headers) rather than
just checking that a URL responds — that is what reliably catches the
"channel shows only a logo" case.

```bash
# requires ffmpeg + ffprobe on PATH and Python 3.8+
python test_playlist.py                 # test ZUL-IPTV.m3u and print a report
python test_playlist.py --prune         # rewrite the playlist, dropping dead channels
python test_playlist.py --workers 1     # definitive check of a flaky channel
python test_playlist.py --min-frames 40 # stricter pass threshold
```

A channel passes only if ffmpeg decodes at least `--min-frames` (default 25)
frames within the time limit. Note that running many decodes in parallel is
CPU-heavy and can cause false `TIMEOUT`s; re-check anything suspicious with
`--workers 1`.

## Notes

- Major Indonesian commercial channels (RCTI, SCTV, Trans TV/7, ANTV, Metro TV,
  tvOne, iNews, Kompas, Moji) are **not included**: in this free public source
  they are dead or DRM/geo-locked and fail the decode test. They are generally
  only available via licensed apps (Vidio, RCTI+, etc.).
- **TVP Sport** was requested but its stream in this source does not play (0
  frames decoded), so it was left out. Re-run `test_playlist.py` later in case
  it comes back, or substitute another working sports channel.
- World Cup 2026 live-match availability on these free streams is not
  guaranteed; the actual Indonesian rights holder may be EMTEK / Vidio.

Source lists:
- Indonesia: https://iptv-org.github.io/iptv/languages/ind.m3u
- Sports: https://iptv-org.github.io/iptv/categories/sports.m3u
- Movies: https://iptv-org.github.io/iptv/categories/movies.m3u
