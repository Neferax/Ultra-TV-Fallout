#include <Arduino.h>
#include <AnimatedGIF.h>
#include "gif_player.h"

// Compile-time guard for the full GIF LZW dictionary.
// The decoder is allocated from the normal heap only when the runtime guard allows it.
static_assert(MAX_CODE_SIZE == 12, "GIF decoder must support the full 12-bit LZW dictionary");
static_assert(MAX_WIDTH == 240, "AnimatedGIF width limit must match the SmallTV display");
static_assert(sizeof(AnimatedGIF) <= 24576, "GIF decoder exceeds the guarded 24 KiB instance budget");

size_t smalltvGifDecoderInstanceSize() {
    return gifPlayerDecoderBytes();
}
