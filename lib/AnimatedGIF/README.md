# Local AnimatedGIF decoder

This is a vendored copy of bitbank2/AnimatedGIF, licensed under Apache-2.0.
It is deliberately configured for this 240x240 ESP8266 target:

- `MAX_CODE_SIZE=10`: GIF files must be specially encoded to stay within 10-bit LZW codes.
- `MAX_WIDTH=240`: larger GIF canvases are rejected.

Do not replace this copy with an unmodified upstream version without repeating
the memory and compile checks. The decoder is not yet connected to LittleFS,
TFT_eSPI, album upload, or the dashboard rotation. It is currently only a
compile-probe dependency.

The source license is included in `LICENSE`.
