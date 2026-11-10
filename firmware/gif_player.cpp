#include "gif_player.h"

#include <LittleFS.h>
#include <umm_heap_select.h>
#include <new>
#include <AnimatedGIF.h>

namespace {
constexpr int kDisplayWidth = 240;
constexpr int kDisplayHeight = 240;
constexpr uint32_t kIramSafetyMargin = 2048;

AnimatedGIF *decoder = nullptr;
File activeGifFile;
TFT_eSPI *targetDisplay = nullptr;
uint32_t nextFrameAtMs = 0;
int16_t canvasOriginX = 0;
int16_t canvasOriginY = 0;
uint16_t scanline565[kDisplayWidth];

void *openGifFile(const char *path, int32_t *fileSize) {
    if (activeGifFile) activeGifFile.close();
    activeGifFile = LittleFS.open(path, "r");
    if (!activeGifFile) return nullptr;
    *fileSize = static_cast<int32_t>(activeGifFile.size());
    return &activeGifFile;
}

void closeGifFile(void *handle) {
    File *file = static_cast<File *>(handle);
    if (file != nullptr && *file) file->close();
}

int32_t readGifFile(GIFFILE *gifFile, uint8_t *buffer, int32_t length) {
    if (gifFile == nullptr || gifFile->fHandle == nullptr || length <= 0) return 0;
    File *file = static_cast<File *>(gifFile->fHandle);
    if (!*file) return 0;
    const int32_t bytesRead = static_cast<int32_t>(file->read(buffer, static_cast<size_t>(length)));
    gifFile->iPos += bytesRead;
    return bytesRead;
}

int32_t seekGifFile(GIFFILE *gifFile, int32_t position) {
    if (gifFile == nullptr || gifFile->fHandle == nullptr || position < 0) return -1;
    File *file = static_cast<File *>(gifFile->fHandle);
    if (!*file || !file->seek(static_cast<uint32_t>(position), SeekSet)) return -1;
    gifFile->iPos = position;
    return position;
}

void drawGifScanline(GIFDRAW *line) {
    if (line == nullptr || targetDisplay == nullptr || line->pPixels == nullptr ||
        line->pPalette == nullptr) return;

    const int16_t x = static_cast<int16_t>(canvasOriginX + line->iX);
    const int16_t y = static_cast<int16_t>(canvasOriginY + line->iY + line->y);
    if (y < 0 || y >= kDisplayHeight) return;

    int sourceX = max(0, -static_cast<int>(x));
    int sourceEnd = min(line->iWidth, kDisplayWidth - static_cast<int>(x));
    if (sourceEnd <= sourceX) return;

    while (sourceX < sourceEnd) {
        if (line->ucHasTransparency && line->pPixels[sourceX] == line->ucTransparent) {
            ++sourceX;
            continue;
        }

        const int runStart = sourceX;
        int runLength = 0;
        while (sourceX < sourceEnd &&
               !(line->ucHasTransparency && line->pPixels[sourceX] == line->ucTransparent)) {
            scanline565[runLength++] = line->pPalette[line->pPixels[sourceX]];
            ++sourceX;
        }

        if (runLength > 0) {
            targetDisplay->pushImage(x + runStart, y, runLength, 1, scanline565);
        }
    }

    // Yield once per decoded row so a large frame cannot monopolise the ESP8266 loop.
    yield();
}
}  // namespace

bool gifPlayerStart(const char *path, TFT_eSPI &display) {
    gifPlayerStop();
    if (path == nullptr || path[0] != '/') return false;

    uint32_t iramFree = 0;
    uint32_t iramLargest = 0;
    {
        HeapSelectIram selected;
        ESP.getHeapStats(&iramFree, &iramLargest);
    }

    const size_t required = sizeof(AnimatedGIF) + kIramSafetyMargin;
    if (iramLargest < required || iramFree < required) return false;

    {
        // ESP8266's selected secondary heap backs this decoder instance only.
        HeapSelectIram selected;
        decoder = new (std::nothrow) AnimatedGIF();
    }
    if (decoder == nullptr) return false;

    targetDisplay = &display;
    decoder->begin(GIF_PALETTE_RGB565_LE);
    if (!decoder->open(path, openGifFile, closeGifFile, readGifFile, seekGifFile, drawGifScanline)) {
        gifPlayerStop();
        return false;
    }

    canvasOriginX = static_cast<int16_t>((kDisplayWidth - decoder->getCanvasWidth()) / 2);
    canvasOriginY = static_cast<int16_t>((kDisplayHeight - decoder->getCanvasHeight()) / 2);
    nextFrameAtMs = 0;
    return true;
}

bool gifPlayerTick(uint32_t nowMs) {
    if (decoder == nullptr) return false;
    if (static_cast<int32_t>(nowMs - nextFrameAtMs) < 0) return false;

    int delayMs = 100;
    const int result = decoder->playFrame(false, &delayMs, nullptr);
    if (result < 0) {
        gifPlayerStop();
        return false;
    }

    if (delayMs < 20) delayMs = 20;
    if (delayMs > 5000) delayMs = 5000;
    nextFrameAtMs = nowMs + static_cast<uint32_t>(delayMs);
    yield();
    return true;
}

void gifPlayerStop() {
    if (decoder != nullptr) {
        decoder->close();
        {
            HeapSelectIram selected;
            delete decoder;
        }
        decoder = nullptr;
    }
    if (activeGifFile) activeGifFile.close();
    targetDisplay = nullptr;
    nextFrameAtMs = 0;
    canvasOriginX = 0;
    canvasOriginY = 0;
}

bool gifPlayerIsActive() {
    return decoder != nullptr;
}

size_t gifPlayerDecoderBytes() {
    return sizeof(AnimatedGIF);
}
