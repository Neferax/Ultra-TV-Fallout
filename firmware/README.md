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

## Not implemented yet

- Animated GIF carousel / stock SmallTV album compatibility.
- Automatic migration of existing stock firmware settings and stored GIFs.
- Device-specific first-flash/recovery procedure for the user's exact board revision.

The upstream firmware currently documents temporary JPEG image rendering and
clears `/image/` on boot. Therefore this patch must **not** be treated as a
replacement that already preserves the stock GIF album. No device flash has
been performed, and this patch has not been compiled or hardware-tested.
