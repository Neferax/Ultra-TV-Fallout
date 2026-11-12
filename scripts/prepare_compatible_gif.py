#!/usr/bin/env python3
"""Convert a GIF into the SmallTV player's supported opaque full-frame format."""
from pathlib import Path
import sys

from PIL import Image, ImageSequence

MAX_BYTES = 300 * 1024
SIZE = (104, 104)
MAX_FRAMES = 36


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_compatible_gif.py INPUT.gif OUTPUT.gif")

    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    target.parent.mkdir(parents=True, exist_ok=True)

    frames = []
    durations = []
    with Image.open(source) as image:
        if image.format != "GIF":
            raise SystemExit("Input is not a GIF")
        if image.width <= 0 or image.height <= 0 or image.width > 240 or image.height > 240:
            raise SystemExit(f"Unsupported source canvas: {image.size}")

        for frame in ImageSequence.Iterator(image):
            rgba = frame.convert("RGBA")
            background = Image.new("RGBA", image.size, (0, 0, 0, 255))
            background.alpha_composite(rgba)
            gray = background.convert("L").resize(SIZE, Image.Resampling.LANCZOS)
            indexed = gray.quantize(colors=64, method=Image.Quantize.MEDIANCUT)
            palette = []
            for value in range(256):
                green = value * 255 // 63 if value < 64 else 0
                palette.extend((0, green, 0))
            indexed.putpalette(palette)
            frames.append(indexed)
            durations.append(max(20, int(frame.info.get("duration", image.info.get("duration", 100)))))

    if not frames:
        raise SystemExit("GIF contains no frames")

    # Keep the archive lightweight while retaining the motion across the loop.
    if len(frames) > MAX_FRAMES:
        selected = []
        selected_durations = []
        step = len(frames) / MAX_FRAMES
        for slot in range(MAX_FRAMES):
            start = int(slot * step)
            end = int((slot + 1) * step)
            selected.append(frames[min(start, len(frames) - 1)])
            selected_durations.append(sum(durations[start:end]))
        frames = selected
        durations = selected_durations

    frames[0].save(
        target,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )

    if target.stat().st_size > MAX_BYTES:
        target.unlink(missing_ok=True)
        raise SystemExit(f"Converted GIF exceeds 300 KiB: {target.stat().st_size} bytes")

    # Re-open the result and verify the logical canvas and opaque full-frame output.
    with Image.open(target) as check:
        if check.size != SIZE or check.info.get("transparency") is not None:
            raise SystemExit("Converted GIF is not an opaque 104x104 canvas")
        count = 0
        for index in range(getattr(check, "n_frames", 1)):
            check.seek(index)
            if check.size != SIZE or check.info.get("transparency") is not None:
                raise SystemExit(f"Frame {index} has unsupported canvas or transparency")
            if check.tile:
                extent = check.tile[0][1]
                if extent != (0, 0, SIZE[0], SIZE[1]):
                    raise SystemExit(f"Frame {index} is partial: {extent}")
            count += 1

    print(f"Compatible GIF: {target} ({target.stat().st_size} bytes, {count} full opaque frames)")


if __name__ == "__main__":
    main()
