# ZUL-IPTV

A hand-curated IPTV playlist (`ZUL-IPTV.m3u`) for use on Samsung TV (and any
M3U-compatible player) from the Jakarta / Bekasi area. **Every channel is
verified to decode real, moving video** — the tester runs ffmpeg *and*
`freezedetect`, so channels that merely show a frozen logo / standby slate (a
common cause of the "logo only, no picture" problem) are rejected too.

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

- **Indonesia** – Nusantara TV, Magna Channel, ROCK Action, Nickelodeon Asia,
  Indonesiana.TV, Jawa Pos TV, Music Information Channel, Stara TV, JTV,
  Bandung TV, Jogja Istimewa TV.
- **Sports - World Cup 2026** – FIFA+ (several languages), beIN Sports USA /
  XTRA, SPOTV / SPOTV 2, Star Sports 1 HD, Alkass One, ARD / Das Erste (German
  FTA World Cup broadcaster, international feed).
- **Sports** – Real Madrid TV, Sportitalia, SuperTennis, Win Sports, NHL
  Network, Red Bull TV, Polsat Sport.
- **Movies** – AMC, IFC, SYFY, Paramount Network, AXN, Starz Cinema, Lifetime
  Movies, Rakuten Top/Action/Comedy/Drama Movies UK, MovieSphere, Runtime, the
  Pluto TV movie channels, Gravitas Movies.

## Testing mechanism (`test_playlist.py`)

IPTV streams are community-maintained and go offline without notice. Use the
included tester to re-verify the playlist at any time. It **decodes video with
ffmpeg and runs `freezedetect`** (honouring each channel's user-agent / referrer
headers) rather than just checking that a URL responds. Each channel is
classified as:

- `OK` – decoded real, moving video
- `STATIC` – decoded video, but it's a frozen logo / standby slate (rejected)
- `DEAD` – no video decoded (stream dead or geo-blocked)
- `TIMEOUT` / `ERR` – did not finish / other error

The `STATIC` check is what catches the "channel shows only a logo" case (e.g.
TVRI was serving a static logo even though frames were arriving).

```bash
# requires ffmpeg + ffprobe on PATH and Python 3.8+
python test_playlist.py                 # test ZUL-IPTV.m3u and print a report
python test_playlist.py --prune         # rewrite the playlist, dropping bad channels
python test_playlist.py --workers 1     # definitive check of a flaky channel
python test_playlist.py --seconds 30    # longer sample (more reliable freeze check)
```

Note that running many decodes in parallel is CPU-heavy and can cause false
`TIMEOUT`s; re-check anything suspicious with `--workers 1`.

## Notes

- Major Indonesian commercial channels (RCTI, SCTV, Trans TV/7, ANTV, Metro TV,
  tvOne, iNews, Kompas, Moji) are **not included**: in this free public source
  they are dead or DRM/geo-locked and fail the decode test. They are generally
  only available via licensed apps (Vidio, RCTI+, etc.).
- World Cup 2026 live-match availability on these free streams is not
  guaranteed; the actual Indonesian rights holder may be EMTEK / Vidio.
- **Requested satellite channels:** of the European / Turkish FTA World Cup
  broadcasters checked (SRF zwei, RTS 2, RSI La 2, TVP Sport, TVP1, Sport1,
  M4 Sport, TRT 1, ARD, ZDF, Arena Premium 1, Sport Klub), only **ARD / Das
  Erste** has a stream that plays from Indonesia (its `/int/` international
  feed). The Swiss SRF/RTS/RSI channels are not in iptv-org at all; the rest are
  geo-locked to their home country and decode 0 frames here. They can't be
  fixed from this free source — they'd require a paid IPTV provider or a VPN
  exit in the relevant country.

Source lists:
- Indonesia: https://iptv-org.github.io/iptv/languages/ind.m3u
- Sports: https://iptv-org.github.io/iptv/categories/sports.m3u
- Movies: https://iptv-org.github.io/iptv/categories/movies.m3u
