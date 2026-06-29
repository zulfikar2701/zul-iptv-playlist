# ZUL-IPTV

A hand-curated IPTV playlist (`ZUL-IPTV.m3u`) for use on Samsung TV (and any
M3U-compatible player) from the Jakarta / Bekasi area.

## How to use on a Samsung TV

1. Use the **raw** URL of `ZUL-IPTV.m3u` from this repo, e.g.
   `https://raw.githubusercontent.com/<user>/ZUL-IPTV/main/ZUL-IPTV.m3u`
2. Open an M3U player app on the TV (e.g. **IPTV Smarters**, **OTT Navigator**,
   **Tivimate**, or Samsung's media player via USB) and import the file/URL.
   You can also copy `ZUL-IPTV.m3u` to a USB stick and open it directly.

## Curation criteria

Channels were selected from the [iptv-org](https://github.com/iptv-org/iptv)
public lists (Indonesian, Sports, Movies) according to:

1. **Playable from Indonesia / Jakarta / Bekasi** – every stream was probed from
   a Bekasi connection and only streams that actually responded were kept.
2. **Popular** – well-known national and international channels only.
3. **High quality content** – film channels that air recent / popular titles
   rather than random B-movies.
4. **World Cup 2026** – includes likely broadcasters / official channels
   (FIFA+, FOX Sports, beIN Sports, Star Sports).
5. **Under 50 channels total.**

## Groups

- **Indonesia** – national news & entertainment (Metro TV, tvOne, CNBC Indonesia,
  TVRI, RRI Net, Nickelodeon Asia, etc.)
- **Sports - World Cup 2026** – FIFA+, FOX Sports, beIN Sports, Star Sports.
- **Sports** – Real Madrid TV, Tennis Channel, Red Bull TV, Sportitalia, etc.
- **Movies** – AMC, AXN, IFC, Paramount Network, SYFY, MovieSphere, etc.

## Notes

IPTV streams are community-maintained and can go offline without notice. If a
channel stops working it can simply be removed/replaced from the source lists.

Source lists:
- Indonesia: https://iptv-org.github.io/iptv/languages/ind.m3u
- Sports: https://iptv-org.github.io/iptv/categories/sports.m3u
- Movies: https://iptv-org.github.io/iptv/categories/movies.m3u
