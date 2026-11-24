# Fallout / Pip-Boy firmware integration

This repository contains source patches and a constrained GIF player for the
open-source ESP8266 firmware
[`iodn/geekmagic-tv-esp8266`](https://github.com/iodn/geekmagic-tv-esp8266).
It does **not** yet contain a verified flash-ready binary.

## Design

- Clock and weather renderers use RobCo / Vault-Tec terminal framing.
- Live NTP time and Open-Meteo weather data paths are retained.
- The built-in Terminal theme (theme ID 2) is selected by default and provides the green-on-dark baseline. The default page rotation interval is 20 seconds.
- Open-Meteo weather is enabled by default for postal area 47239 Duisburg (Rumeln-Kaldenhausen).
- The default clock zone is Europe/Berlin with automatic CET/CEST daylight-saving changes; other fixed offsets remain configurable.
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
- Full 12-bit LZW code size (`MAX_CODE_SIZE=12`).
- Every frame must cover the full canvas and be opaque. Partial or transparent frames are rejected by the runtime player.
- No full-canvas compositing buffer is allocated. All source colors are tinted to monochrome Pip-Boy green. The bundled Vault Boy GIF is pre-converted to opaque full-canvas frames.

The decoder instance is allocated with `new (std::nothrow)` from the normal ESP8266 heap only during GIF playback. Before allocation, the player checks for at least `sizeof(AnimatedGIF) + 8192` bytes of reported free heap. The decoder is released before feed/TLS work, OTA upload and pending network actions. This runtime guard is not proof of stability under every Wi-Fi, web-server and TLS load; actual heap behavior still requires testing on the device.

## Installation caveats

The Stock SmallTV firmware's existing `/gif` and `/image` files are not
automatically migrated into the new LittleFS. Back up all originals outside
the device before changing firmware, then upload compatible files through the
new `/gif` page after installation.

The exact board revision, flash partition layout, first-flash method, and
recovery procedure still need verification. Wi-Fi credentials from the Stock
firmware are not guaranteed to migrate; the upstream failsafe access point may
be needed to configure the new firmware. No firmware has been flashed and
no device files have been changed.

## Validation status

The GitHub Actions workflow checks the expected upstream renderer source,
applies both patches, copies the decoder/player sources, and runs
`pio run -e nodemcuv2`. Build 376 completed successfully and produced the firmware, OTA loader and installation package. The native 240×240 renderer audit also passed, including the graphical Celsius degree marks. Static/native checks do not establish real-device operation. The exact board revision, partition layout, first-flash method, recovery path, and hardware behavior still require verification; this is not yet hardware-approved.
