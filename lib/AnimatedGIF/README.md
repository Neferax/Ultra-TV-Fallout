# Local AnimatedGIF decoder

Vendored copy of [bitbank2/AnimatedGIF](https://github.com/bitbank2/AnimatedGIF),
licensed under Apache-2.0. The original license is included in `LICENSE`.

The library is deliberately configured for the 240×240 ESP8266 target:
- `MAX_CODE_SIZE=11`: LZW dictionary codes are limited to 11 bits.
- `MAX_WIDTH=240`: frame width is limited to the display width.
- The player separately rejects a canvas height above 240 pixels.
- A compile probe enforces an `AnimatedGIF` instance size no greater than
  15,360 bytes.

The player implementation lives in `firmware/gif_player.cpp/.h`. It streams
from LittleFS and draws RAW RGB565 scanlines directly to TFT_eSPI. It does not
allocate the library's full-canvas framebuffer or Turbo buffer.

The player requires every frame to cover the complete GIF canvas. Transparent
pixels are flattened to black, and source colors are converted to monochrome
Pip-Boy green. Since every frame redraws the whole canvas, all disposal methods
are accepted without keeping a compositing buffer. Partial-frame animations
are rejected to avoid trails and stale pixels.

Do not replace this constrained copy with an unmodified upstream version
without repeating the memory and compile checks.
