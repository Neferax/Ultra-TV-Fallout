# Alternative firmware base audit — 10.11.2026

## Candidate selected for source-level Fallout UI work

Repository: https://github.com/iodn/geekmagic-tv-esp8266

This is a source-available ESP8266 firmware that explicitly reports testing on the GeekMagic SmallTV Ultra. It has the same 240×240 ST7789 display target, live NTP clock, Open-Meteo weather feed, LittleFS, a web dashboard, and independently rendered clock/weather pages.

Unlike a theme package, its display renderer is source code:
- `src/display.cpp`: `renderClockPage()`, `renderWeatherPage()`, shared `drawScreenChrome()`, typography and page rendering.
- `src/dashboard.h`: page IDs and weather data model.
- `src/feeds.h`: weather provider configuration and runtime data.
- `src/device-themes.json`: existing palette definitions.
- `platformio.ini`: ESP8266 / ESP-12F target, 240×240 ST7789 and TFT_eSPI pin configuration.

This is a materially better source base for a real UI redesign than smalltv-mod's declarative clock theme. The weather renderer already receives live temperature, high/low, rain chance, condition and location; the clock renderer has live NTP time/date and can show the current weather as a secondary block.

## Hardware / installation caveat

The upstream README documents a first installation by serial flashing and subsequent OTA. The SmallTV Ultra's USB-C connector is power-only according to device documentation and prior device research; its UART pads are internal. Therefore the upstream first-flash instructions must not be assumed to work over the external USB-C port. A serial adapter / internal pads may be required for the first install.

The upstream project has been tested on a SmallTV Ultra, but this project has not yet been built or flashed on the user's unit. No binary should be offered as flash-ready until the exact board pin map, flash layout, OTA partition behaviour and recovery path are verified.

## Fallout UI implementation plan

Target remains exactly two data pages and the existing animation/GIF flow:
- Clock page: black background, monochrome Pip-Boy phosphor green, RobCo system header, oversized high-contrast time, date/weekday, subtle segmented rules and a small weather/status strip.
- Weather page: RobCo weather terminal header, large current temperature, readable condition/location, separate HIGH / LOW / RAIN data blocks, simple green weather glyphs and no tiny low-contrast text.
- Page rotation: retain only CLOCK and WEATHER; disable all other optional dashboard pages in configuration.
- Existing GIF sequence: assess whether the replacement firmware can support the current GIF storage/rotation. The candidate source currently documents temporary JPEG image rendering and clears `/image/` at boot, so it does **not** preserve the stock GIF carousel as-is. This must be implemented deliberately before choosing it as the final base.

## Current conclusion

The candidate firmware provides a practical source-level route to redesign the clock and weather renderers, but it is not yet a drop-in replacement for the full requested experience because the stock GIF carousel is not preserved. The next code work should prototype the Fallout renderers and separately specify GIF animation storage/playback before any device installation is considered.

No device writes, deletes, firmware updates or flash operations have been performed.
