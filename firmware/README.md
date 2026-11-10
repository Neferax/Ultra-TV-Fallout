# Fallout / Pip-Boy firmware integration

This repository contains source patches and a constrained GIF player for the
open-source ESP8266 firmware
[`iodn/geekmagic-tv-esp8266`](https://github.com/iodn/geekmagic-tv-esp8266).
It does **not** yet contain a verified flash-ready binary.

## Design

- Clock and weather renderers use RobCo / Vault-Tec terminal framing.
- Live NTP time and Open-Meteo weather data paths are retained.
- The built-in Terminal theme (theme ID 2) provides the green-on-dark baseline.
- The existing Status page slot is reused as the GIF archive page immediately
  after Weather. No extra dashboard page is added.
- Only Clock, Weather and GIF are enabled by default.

Suggested custom colors:
- background: `#020A03`
- surface: `#071A0A`
- accent: `#39FF6A`
- text: `#9BFFAE`

## Source files

- `patches/0001-fallout-pipboy-renderers.patch`: Clock and Weather UI.
- `patches/0002-gif-player-integration.patch`: GIF page, upload route,
  rotation integration, and feed/OTA memory scheduling.
- `firmware/gif_player.cpp/.h`: LittleFS-to-TFT scanline player.
- `lib/AnimatedGIF/`: vendored Apache-2.0 decoder with ESP8266 memory limits.
- `firmware/gif_decoder_probe.cpp`: compile-time decoder size guard.
- `.github/workflows/smalltv-firmware-build.yml`: reproducible upstream patch
  application and PlatformIO build.

## GIF album

After a successful firmware installation, open
`http://<device-ip>/gif` and upload compatible animations. Files are stored in
LittleFS at `/gif/`. Uploads validate the GIF signature and canvas size, use a
temporary file, and replace an existing filename only after the full upload
succeeds.

Limits:
- Canvas up to 240×240 pixels.
- Up to twelve indexed GIF files.
- 300 KiB maximum per file.
- LZW code size up to 11 bits.
- Every frame must be opaque and cover the full canvas.
- Transparent or partial frames are rejected; no full-canvas compositing buffer
  is allocated.

The decoder instance is allocated in the secondary IRAM heap only during GIF
playback. It is released before feed/TLS work, OTA upload and pending network
actions. If the IRAM block is too small, the GIF page is skipped rather than
falling back to DRAM.

## Installation caveats

The Stock SmallTV firmware's existing `/gif` and `/image` files are not
automatically migrated into the new LittleFS. Back up all originals outside
the device before changing firmware, then upload compatible files through the
new `/gif` page after installation.

The exact board revision, flash partition layout, first-flash method, and
recovery procedure still need verification. No firmware has been flashed and
no device files have been changed.

## Validation status

The GitHub Actions workflow checks the expected upstream renderer source,
applies both patches, copies the decoder/player sources, and runs
`pio run -e nodemcuv2`. A successful workflow result has not yet been confirmed.
Until the build and hardware tests pass, this is a source prototype, not a
flash-ready release.
