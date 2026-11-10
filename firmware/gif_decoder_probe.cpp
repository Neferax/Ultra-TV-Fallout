#include <Arduino.h>
#include <AnimatedGIF.h>

// Compile-time guard for the intentionally constrained decoder build.
// The GIF assets must be re-encoded so their LZW code size never exceeds 10 bits.
static_assert(MAX_CODE_SIZE == 10, "Unexpected AnimatedGIF LZW memory configuration");
static_assert(MAX_WIDTH == 240, "AnimatedGIF width limit must match the SmallTV display");

size_t smalltvGifDecoderInstanceSize() {
    return sizeof(AnimatedGIF);
}
