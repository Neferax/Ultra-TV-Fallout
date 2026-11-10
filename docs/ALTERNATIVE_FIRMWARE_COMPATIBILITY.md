# Alternative firmware compatibility decision — 10.11.2026

## Device facts
- Device: GeekMagic SmallTV Ultra
- Stock firmware: Ultra-V9.0.50
- Device IP: 192.168.178.70
- Existing display flow the user wants to preserve: stock weather page, stock clock page, and the existing GIF pages between them.
- Filesystem free space last reported by the device: 187,916 bytes.

## Finding: smalltv-mod is not a drop-in visual theme for stock Ultra
The current `giovi321/smalltv-mod` project is an alternative firmware that replaces the stock firmware. Its theme-clock engine draws a replacement clock face inside smalltv-mod; it does not patch the stock GeekMagic weather page, stock clock page, or stock GIF carousel.

The upstream theme system can draw a 240×240 clock face using text, shapes, images, animations and limited JSON data sources. It is not a general-purpose skin for the original Ultra-V9.0.50 UI. Therefore, a `.stheme` package alone cannot deliver the requested complete redesign of the existing stock pages.

The alternative firmware also requires a two-step loader install on the SmallTV Ultra because the stock Ultra OTA partition is too small for the full firmware. This is a materially different and riskier operation than uploading a GIF or changing a stock setting.

## Decision
Do **not** install smalltv-mod or its loader as a shortcut. Do not build a standalone `.stheme` and present it as a complete stock-firmware redesign.

The implementation target remains the stock Ultra-V9.0.50 page flow:
1. Weather page: rebuild its visible layout in a Pip-Boy/RobCo style while retaining live weather data.
2. Clock page: rebuild its visible layout in the same style while retaining live time/date.
3. Existing GIF slots: use matching green monochrome Fallout-inspired animations, retaining the current carousel/order.
4. Preserve the current Wi-Fi and device configuration.

## Technical blocker
The stock GeekMagic V9.0.50 source code and its page-rendering implementation have not been obtained. The official firmware repository publishes firmware packages and changelogs, not the full source tree. The device's exposed JSON endpoints so far describe settings, storage and file lists; they do not establish a supported API for changing the native weather/clock drawing code.

A genuine firmware-level redesign therefore requires one of:
- obtaining the matching V9.0.50 source/build system from the vendor; or
- reverse-engineering the exact V9.0.50 firmware binary and safely patching/rebuilding its UI code; or
- writing a replacement firmware that deliberately recreates the required weather, clock and GIF carousel behaviour.

The third option is not equivalent to a theme upload and needs a full feature/compatibility audit before any flash.

## Safety / acceptance criteria
- No flash, erase, loader install, or destructive file operation without a verified recovery path and a full original backup.
- No claim that a build is flash-ready until it has compiled for the exact ESP8266/ESP-12F target and passed static validation.
- No fake weather or fixed clock values in the final interface.
- No new external service requirement unless the user explicitly accepts it.
- First milestone is a verified stock UI customization route or a technically complete replacement architecture, not another mockup or GIF-only package.

## Research references
- smalltv-mod README and theme support: https://github.com/giovi321/smalltv-mod
- Theme engine specification: https://giovi321.github.io/smalltv-mod/features/themes/
- SmallTV Ultra install constraints: https://giovi321.github.io/smalltv-mod/getting-started/flashing/
- Official GeekMagic firmware repository: https://github.com/GeekMagicClock/smalltv-ultra
