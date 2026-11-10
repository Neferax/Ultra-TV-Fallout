#include <Arduino.h>
#include <AnimatedGIF.h>
#include "gif_player.h"

// Compile-time guard for the intentionally constrained decoder build.
// GIF assets must be re-encoded so their LZW code size never exceeds 10 bits.
static_assert(MAX_CODE_SIZE == 11, "Unexpected AnimatedGIF LZW memory configuration");
static_assert(MAX_WIDTH == 240, "AnimatedGIF width limit must match the SmallTV display");
static_assert(sizeof(AnimatedGIF) <= 15360, "GIF decoder exceeds the 15 KiB instance budget");

size_t smalltvGifDecoderInstanceSize() {
    return gifPlayerDecoderBytes();
}
