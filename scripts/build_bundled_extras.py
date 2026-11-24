#!/usr/bin/env python3
"""Build the extra bundled GIFs for the RADIO page rotation.

The constrained GIF decoder on the SmallTV needs full-canvas 104x104 opaque
frames with a global palette, at most 36 frames and at most 300 KiB per file.
This script downloads the two source animations from Tenor, picks the frames
that play best on the 104x104 viewport, and writes the two GIFs the embed
script installs into the firmware.

Usage: python scripts/build_bundled_extras.py out/nuka-cola.gif out/vault-boy-clap.gif
"""
import sys
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image, ImageSequence

RESAMPLE = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
DITHER_NONE = getattr(getattr(Image, "Dither", None), "NONE", 0)
SIZE = (104, 104)
COLORS = 64
MAX_BYTES = 300 * 1024

NUKA_URL = "https://media1.tenor.com/m/Cpp8sZliEVwAAAAW/fallout-nuka-cola.gif"
CLAP_URL = "https://media1.tenor.com/m/u3q86VtyfjkAAAAW/dab-vault-boy.gif"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"

# nuka: six frames spread across the 39-frame logo loop
NUKA_INDICES = [0, 6, 13, 19, 26, 32]
# clap: the Vault Boy puppet clap sits at frames 86-97 of the clip
CLAP_INDICES = [86, 87, 88, 90, 92, 93, 95, 97]
FALLBACK_DURATION_MS = 100


def load_frames(path):
    frames = []
    with Image.open(path) as source:
        for frame in ImageSequence.Iterator(source):
            duration = int(frame.info.get("duration", 0) or 0)
            frames.append((frame.convert("RGB"), duration))
    return frames


def download(url, target):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        target.write_bytes(response.read())


def build(source_frames, indices, output):
    picked = [source_frames[i] for i in indices]
    resized = [frame.resize(SIZE, RESAMPLE) for frame, _ in picked]
    durations = [duration if duration > 0 else FALLBACK_DURATION_MS for _, duration in picked]
    strip = Image.new("RGB", (SIZE[0] * len(resized), SIZE[1]))
    for offset, frame in enumerate(resized):
        strip.paste(frame, (offset * SIZE[0], 0))
    palette = strip.quantize(colors=COLORS, method=Image.MEDIANCUT)
    encoded = [
        frame.quantize(palette=palette, dither=DITHER_NONE)
        for frame in resized
    ]
    encoded[0].save(
        output,
        save_all=True,
        append_images=encoded[1:],
        loop=0,
        duration=durations,
        disposal=2,
        optimize=False,
    )


def verify(output):
    size = output.stat().st_size
    unique = set()
    duration = 0
    with Image.open(output) as gif:
        if gif.size != SIZE:
            raise SystemExit(f"{output}: wrong canvas {gif.size}")
        if gif.info.get("transparency") is not None:
            raise SystemExit(f"{output}: transparent frames are not supported")
        count = 0
        for index in range(gif.n_frames):
            gif.seek(index)
            if gif.info.get("transparency") is not None:
                raise SystemExit(f"{output}: frame {index} is transparent")
            if not gif.tile or gif.tile[0][1] != (0, 0, SIZE[0], SIZE[1]):
                raise SystemExit(f"{output}: frame {index} is not full-canvas")
            unique.add(gif.convert("RGB").tobytes())
            duration += gif.info.get("duration", 0)
            count += 1
    if not 2 <= count <= 36 or len(unique) < 2 or duration <= 0:
        raise SystemExit(f"{output}: unusable animation ({count} frames)")
    if size > MAX_BYTES:
        raise SystemExit(f"{output}: {size} bytes exceeds {MAX_BYTES}")
    print(f"built {output}: {count} frames, {len(unique)} unique, {duration} ms, {size} bytes")


def main(argv):
    if len(argv) != 2:
        raise SystemExit(__doc__)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        nuka_src = tmp / "nuka.gif"
        clap_src = tmp / "clap.gif"
        download(NUKA_URL, nuka_src)
        download(CLAP_URL, clap_src)
        nuka = load_frames(nuka_src)
        clap = load_frames(clap_src)
        for indices, source in ((NUKA_INDICES, nuka), (CLAP_INDICES, clap)):
            for index in indices:
                if not 0 <= index < len(source):
                    raise SystemExit(f"frame {index} is outside the source ({len(source)} frames)")
        build(nuka, NUKA_INDICES, Path(argv[0]))
        build(clap, CLAP_INDICES, Path(argv[1]))
    verify(Path(argv[0]))
    verify(Path(argv[1]))


if __name__ == "__main__":
    main(sys.argv[1:])
