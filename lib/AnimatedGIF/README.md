# Local AnimatedGIF decoder

This is a vendored copy of bitbank2/AnimatedGIF, licensed under Apache-2.0.
It is deliberately configured for this 240x240 ESP8266 target:

- `MAX_CODE_SIZE=11`: GIF files must be specially encoded to stay within 11-bit LZW codes.
- `MAX_WIDTH=240`: larger GIF canvases are rejected.

Do not replace this copy with an unmodified upstream version without repeating
the memory and compile checks. The decoder is not yet connected to LittleFS,
TFT_eSPI, album upload, or the dashboard rotation. It is currently only a
compile-probe dependency.

The source license is included in `LICENSE`.

The current player prototype additionally accepts only **flattened full-canvas
frames**: each frame must cover the complete GIF canvas, contain no transparent
pixels, and not rely on disposal method 2. This avoids requiring a full-canvas
compositing buffer, which is too expensive on this ESP8266. Unsupported frames
are rejected rather than displayed with trails or broken transparency.
