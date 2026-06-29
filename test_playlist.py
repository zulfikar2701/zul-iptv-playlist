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


def _frozen_fraction(stderr, total):
    """Fraction of the sample that ffmpeg's freezedetect flagged as frozen."""
    if total <= 0:
        return 0.0
    starts = [float(x) for x in re.findall(r"freeze_start:\s*([\d.]+)", stderr)]
    ends = [float(x) for x in re.findall(r"freeze_end:\s*([\d.]+)", stderr)]
    frozen = 0.0
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else total  # open freeze runs to the end
        frozen += max(0.0, min(e, total) - s)
    return frozen / total


def test_channel(ch, seconds=18, timeout=60, freeze_thresh=0.6):
    """
    Decode the stream with ffmpeg AND run freezedetect.
    Returns (status, frames) where status is one of:
      'OK'      - decoded real, moving video
      'STATIC'  - decoded video but it is a frozen logo / standby slate
      'DEAD'    - no video decoded (stream dead / geo-blocked)
      'TIMEOUT' - ffmpeg did not finish in time
      'ERR'     - other error
    """
    ua, ref = headers(ch)
    args = ["ffmpeg", "-nostdin", "-hide_banner", "-rw_timeout", "15000000"]
    if ua:
        args += ["-user_agent", ua]
    if ref:
        args += ["-headers", f"Referer: {ref}\r\n"]
    args += ["-i", ch["url"], "-t", str(seconds),
             "-vf", "freezedetect=n=-50dB:d=3", "-map", "0:v:0", "-an",
             "-f", "null", "-"]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="ignore")
        frames = [int(x) for x in re.findall(r"frame=\s*(\d+)", p.stderr)]
        f = max(frames) if frames else 0
        if f < 25:
            return "DEAD", f
        tmatch = re.findall(r"time=(\d+):(\d+):([\d.]+)", p.stderr)
        total = 0.0
        if tmatch:
            h, m, s = tmatch[-1]
            total = int(h) * 3600 + int(m) * 60 + float(s)
        if _frozen_fraction(p.stderr, total or seconds) > freeze_thresh:
            return "STATIC", f
        return "OK", f
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1
    except Exception:
        return "ERR", -2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("playlist", nargs="?", default="ZUL-IPTV.m3u")
    # decoding is CPU heavy; too many parallel workers can cause false TIMEOUTs.
    # Use --workers 1 for a definitive check of a flaky channel.
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--seconds", type=int, default=18,
                    help="sample length; longer gives freezedetect more to work with")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--prune", action="store_true",
                    help="rewrite the playlist keeping only working channels")
    args = ap.parse_args()

    channels = parse_m3u(args.playlist)
    print(f"Testing {len(channels)} channels in {args.playlist} "
          f"(decode + freeze check, {args.seconds}s each)\n", flush=True)

    def run(ch):
        status, frames = test_channel(ch, args.seconds, args.timeout)
        return ch, status, frames

    working, results = [], []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for ch, status, frames in ex.map(run, channels):
            ok = status == "OK"
            fr = f"{frames}f" if frames >= 0 else ""
            print(f"{'OK ' if ok else 'XX '} {status:8} {fr:>6}  {ch['name']}",
                  flush=True)
            results.append((ch, ok, status))
            if ok:
                working.append(ch)

    print(f"\nWorking: {len(working)}/{len(channels)}")
    for label in ("STATIC", "DEAD", "TIMEOUT", "ERR"):
        bad = [c["name"] for c, ok, s in results if s == label]
        if bad:
            print(f"{label}:", ", ".join(bad))

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
