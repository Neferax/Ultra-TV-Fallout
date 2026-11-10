# Fallout / Pip-Boy renderer patch

This directory contains a source patch for the upstream ESP8266 firmware
`iodn/geekmagic-tv-esp8266`, not a ready-to-flash firmware image.

## What this patch changes

- Replaces the clock page's generic header with RobCo / Vault-Tec terminal labels.
- Frames the live NTP clock and live weather summary in a monochrome terminal layout.
- Reworks the weather page into a Pip-Boy-style instrument panel.
- Keeps the upstream Open-Meteo data model and time renderer; it does not fake
  weather values or replace live clock data.

The patch uses the upstream theme palette. Select the built-in **Terminal**
palette (theme ID 2) in the web dashboard for the green-on-dark baseline.
For a closer classic Pip-Boy look, use custom colors:
- background: `#020A03`
- surface: `#071A0A`
- accent: `#39FF6A`
- text: `#9BFFAE`

## Apply

From a checkout of the upstream repository:

```sh
git apply patches/0001-fallout-pipboy-renderers.patch
pio run
```

The patch was authored against upstream `src/display.cpp` blob
`ef482ea3cc556eb414fff6178fcc7a4d136563a9`.

## GIF support: current finding

The current upstream source does **not** contain a GIF player. More importantly,
its October 2026 change history records removal of JPEG display, picture uploads,
picture routes, dashboard controls, and the JPEG decoder dependency to recover
RAM. The upstream README still contains older image-upload wording; that wording
does not describe the current source tree.

A GIF player therefore needs to be added as a separate feature. The candidate
AnimatedGIF library can stream decoded scanlines through callbacks without a
full 240x240 RGB565 framebuffer, but its standard decoder object is about 22.5 KB
of RAM. That is a serious fit risk on this firmware: its hardware verification
reports only about 18.5 KB free primary DRAM after normal startup, and the
network/TLS path needs additional reserved headroom.

A safe implementation needs a constrained decoder build, GIF files re-encoded
to a known maximum LZW code size, scanline-only drawing, LittleFS file callbacks,
and a scheduler that pauses animation during feed/TLS work. The user's original
GIF files must first be backed up outside the device before any replacement
firmware is flashed. None of that is implemented yet.

## Not implemented / not verified

- Animated GIF carousel / stock SmallTV album compatibility.
- Automatic migration of existing stock firmware settings and stored GIFs.
- Device-specific first-flash/recovery procedure for the user's exact board revision.
- Patch application, compile, runtime memory profiling, or screen verification.

No device flash or storage modification has been performed.

## GIF archive and player integration (prototype)

The current implementation patch repurposes the existing Status page slot as a
GIF page immediately after Weather in the dashboard rotation; it does not add
a new dashboard page. A protected upload page is available at
`http://<device-ip>/gif`. Uploaded files are stored in LittleFS under
`/gif/`; the upload checks the GIF signature and 240×240 canvas, writes to a
temporary file, and only replaces an existing filename after the complete write succeeds.

The decoder is intentionally constrained for the ESP8266:
- Maximum canvas size: 240×240 pixels.
- Maximum file size: 300 KiB per GIF; at most twelve files are indexed.
- LZW code size must stay at or below 11 bits.
- Frames must be full-canvas and opaque. Transparent or partial frames are
  rejected because the player deliberately avoids a 240x240 compositing buffer.
- The decoder object is allocated from the secondary IRAM heap only while the
  GIF page is active. It is stopped before feed/TLS work, OTA upload and pending
  network actions.

**Important:** this is still a source prototype. The integration patch and
GitHub Actions build workflow exist, but a successful CI build and hardware
playback have not yet been verified. It is not a flash-ready firmware image.

The stock firmware's existing `/gif` and `/image` contents are not migrated
automatically into the new firmware's LittleFS. Back up the original files
separately and upload compatible GIFs through the new `/gif` page after
installation. No files have been changed on the device.
