#!/usr/bin/env python3
"""
Thoroughly test an M3U playlist by actually DECODING video from each stream
with ffmpeg (not just checking that the URL responds). A channel is considered
"playing" only if ffmpeg decodes enough real video frames within the time limit.

This is what catches the "channel shows only a logo" problem: a master playlist
can return HTTP 200 while its actual video segments are dead or geo-blocked.

Requirements: ffmpeg + ffprobe on PATH, Python 3.8+.

Usage:
    python test_playlist.py                 # test ZUL-IPTV.m3u, print a report
    python test_playlist.py other.m3u       # test a different playlist
    python test_playlist.py --prune         # rewrite playlist keeping only working channels
    python test_playlist.py --min-frames 40 # stricter threshold (default 25)
    python test_playlist.py --workers 4     # parallel ffmpeg workers (default 5)
"""
import argparse, json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def parse_m3u(path):
    """Return list of channels: {name, extinf, extra[], url}."""
    lines = open(path, encoding="utf-8").read().splitlines()
    channels, cur = [], None
    for line in lines:
        if line.startswith("#EXTINF"):
            name = line.rsplit(",", 1)[1].strip() if "," in line else ""
            cur = {"name": name, "extinf": line, "extra": [], "url": None}
        elif line.startswith("#") and cur is not None:
            cur["extra"].append(line)
        elif line and not line.startswith("#") and cur is not None:
            cur["url"] = line
            channels.append(cur)
            cur = None
    return channels


def headers(ch):
    """Extract http-user-agent / http-referrer if the channel specifies them."""
    blob = ch["extinf"] + "\n" + "\n".join(ch["extra"])
    ua = ref = None
    m = re.search(r'http-user-agent="?([^"\n]+?)"?(?:\s+[a-z-]+=|$)', blob) or \
        re.search(r"user-agent=([^\n]+)", blob)
    if m:
        ua = m.group(1).strip().strip('"')
    m = re.search(r'http-referrer="?([^"\n]+?)"?(?:\s+[a-z-]+=|$)', blob) or \
        re.search(r"referrer=([^\n]+)", blob)
    if m:
        ref = m.group(1).strip().strip('"')
    return ua, ref


def test_channel(ch, seconds=8, timeout=60):
    """Return (ok, frames_decoded). ok means ffmpeg decoded real video."""
    ua, ref = headers(ch)
    args = ["ffmpeg", "-nostdin", "-hide_banner", "-rw_timeout", "15000000"]
    if ua:
        args += ["-user_agent", ua]
    if ref:
        args += ["-headers", f"Referer: {ref}\r\n"]
    args += ["-i", ch["url"], "-t", str(seconds), "-an", "-f", "null", "-"]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="ignore")
        frames = [int(x) for x in re.findall(r"frame=\s*(\d+)", p.stderr)]
        return (max(frames) if frames else 0), False
    except subprocess.TimeoutExpired:
        return -1, True
    except Exception:
        return -2, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("playlist", nargs="?", default="ZUL-IPTV.m3u")
    ap.add_argument("--min-frames", type=int, default=25)
    # decoding is CPU heavy; too many parallel workers can cause false TIMEOUTs.
    # Use --workers 1 for a definitive check of a flaky channel.
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--seconds", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--prune", action="store_true",
                    help="rewrite the playlist keeping only working channels")
    args = ap.parse_args()

    channels = parse_m3u(args.playlist)
    print(f"Testing {len(channels)} channels in {args.playlist} "
          f"(decoding {args.seconds}s, need >= {args.min_frames} frames)\n", flush=True)

    def run(ch):
        frames, _ = test_channel(ch, args.seconds, args.timeout)
        return ch, frames

    working, results = [], []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for ch, frames in ex.map(run, channels):
            ok = frames >= args.min_frames
            label = ("TIMEOUT" if frames == -1 else "ERR" if frames == -2
                     else f"{frames}f")
            print(f"{'OK ' if ok else 'XX '} {label:>8}  {ch['name']}", flush=True)
            results.append((ch, ok))
            if ok:
                working.append(ch)

    print(f"\nWorking: {len(working)}/{len(channels)}")
    dead = [c["name"] for c, ok in results if not ok]
    if dead:
        print("Not playing:", ", ".join(dead))

    if args.prune:
        out = ["#EXTM3U"]
        for ch in working:
            out.append(ch["extinf"])
            out += ch["extra"]
            out.append(ch["url"])
        open(args.playlist, "w", encoding="utf-8").write("\n".join(out) + "\n")
        print(f"\nPruned {args.playlist} to {len(working)} working channels.")

    sys.exit(0 if len(working) == len(channels) else 1)


if __name__ == "__main__":
    main()
