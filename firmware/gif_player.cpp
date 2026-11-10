#include "gif_player.h"

#include <LittleFS.h>
#include <ESP8266WiFi.h>
#include <umm_heap_select.h>
#include <new>
#include <AnimatedGIF.h>

namespace {
constexpr int kDisplayWidth = 240;
constexpr int kDisplayHeight = 240;
constexpr uint32_t kIramSafetyMargin = 2048;

AnimatedGIF *decoder = nullptr;
File activeGifFile;
File uploadGifFile;
TFT_eSPI *targetDisplay = nullptr;
uint32_t nextFrameAtMs = 0;
uint32_t gifStartedAtMs = 0;
uint32_t uploadGifBytes = 0;
char uploadGifPath[48] = {0};
char uploadGifTempPath[56] = {0};
bool gifFileListDirty = true;
char gifPaths[12][48] = {{0}};
uint8_t gifPathCount = 0;
uint8_t nextGifIndex = 0;
int16_t canvasOriginX = 0;
int16_t canvasOriginY = 0;
int16_t canvasWidth = 0;
int16_t canvasHeight = 0;
bool unsupportedFrame = false;
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
        line->pPalette == nullptr || unsupportedFrame) return;

    // No full-canvas framebuffer is available on this ESP8266. Accept only
    // pre-flattened opaque frames; partial/transparency/disposal-2 frames need
    // compositing state and would otherwise leave trails.
    if (line->ucHasTransparency || line->ucDisposalMethod == 2 ||
        line->iX != 0 || line->iY != 0 ||
        line->iWidth != canvasWidth || line->iHeight != canvasHeight) {
        unsupportedFrame = true;
        return;
    }

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

    canvasWidth = static_cast<int16_t>(decoder->getCanvasWidth());
    canvasHeight = static_cast<int16_t>(decoder->getCanvasHeight());
    if (canvasWidth <= 0 || canvasHeight <= 0 ||
        canvasWidth > kDisplayWidth || canvasHeight > kDisplayHeight) {
        gifPlayerStop();
        return false;
    }
    canvasOriginX = static_cast<int16_t>((kDisplayWidth - canvasWidth) / 2);
    canvasOriginY = static_cast<int16_t>((kDisplayHeight - canvasHeight) / 2);
    unsupportedFrame = false;
    nextFrameAtMs = 0;
    gifStartedAtMs = millis();
    return true;
}

bool gifPlayerTick(uint32_t nowMs) {
    if (decoder == nullptr) return false;
    if (nowMs - gifStartedAtMs >= 20000UL) {
        TFT_eSPI *display = targetDisplay;
        gifPlayerStop();
        if (display != nullptr) gifPlayerStartNext(*display);
        return true;
    }
    if (static_cast<int32_t>(nowMs - nextFrameAtMs) < 0) return false;

    int delayMs = 100;
    const int result = decoder->playFrame(false, &delayMs, nullptr);
    if (result < 0 || unsupportedFrame) {
        if (targetDisplay != nullptr) targetDisplay->fillScreen(TFT_BLACK);
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
    gifStartedAtMs = 0;
    canvasOriginX = 0;
    canvasOriginY = 0;
    canvasWidth = 0;
    canvasHeight = 0;
    unsupportedFrame = false;
}

bool gifPlayerIsActive() {
    return decoder != nullptr;
}

size_t gifPlayerDecoderBytes() {
    return sizeof(AnimatedGIF);
}


bool gifPlayerRefreshFiles() {
    gifPathCount = 0;
    Dir dir = LittleFS.openDir("/gif");
    while (dir.next() && gifPathCount < 12) {
        String name = dir.fileName();
        if (!name.endsWith(".gif") && !name.endsWith(".GIF")) continue;
        if (dir.fileSize() == 0 || dir.fileSize() > 300UL * 1024UL) continue;

        String path = name.startsWith("/") ? name : String("/gif/") + name;
        if (path.length() >= sizeof(gifPaths[0])) continue;
        path.toCharArray(gifPaths[gifPathCount], sizeof(gifPaths[0]));
        ++gifPathCount;
    }

    // Keep album order deterministic regardless of LittleFS directory order.
    for (uint8_t i = 0; i < gifPathCount; ++i) {
        for (uint8_t j = i + 1; j < gifPathCount; ++j) {
            if (strcmp(gifPaths[j], gifPaths[i]) < 0) {
                char swap[48];
                memcpy(swap, gifPaths[i], sizeof(swap));
                memcpy(gifPaths[i], gifPaths[j], sizeof(swap));
                memcpy(gifPaths[j], swap, sizeof(swap));
            }
        }
    }
    if (nextGifIndex >= gifPathCount) nextGifIndex = 0;
    gifFileListDirty = false;
    return gifPathCount > 0;
}

bool gifPlayerHasFiles() {
    if (gifFileListDirty) gifPlayerRefreshFiles();
    return gifPathCount > 0;
}

bool gifPlayerStartNext(TFT_eSPI &display) {
    if (gifFileListDirty) gifPlayerRefreshFiles();
    if (gifPathCount == 0) return false;

    const uint8_t selected = nextGifIndex;
    nextGifIndex = static_cast<uint8_t>((nextGifIndex + 1) % gifPathCount);
    return gifPlayerStart(gifPaths[selected], display);
}

bool gifPlayerUploadStart(const char *filename) {
    gifPlayerStop();
    if (filename == nullptr || filename[0] == '\0') return false;

    String name(filename);
    int slash = max(name.lastIndexOf('/'), name.lastIndexOf('\\'));
    if (slash >= 0) name = name.substring(slash + 1);
    if (name.length() == 0 || name.length() > 36 ||
        (!name.endsWith(".gif") && !name.endsWith(".GIF"))) return false;

    for (size_t i = 0; i < name.length(); ++i) {
        const char ch = name[i];
        const bool valid = (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') ||
                           (ch >= '0' && ch <= '9') || ch == '-' || ch == '_' || ch == '.';
        if (!valid) return false;
    }

    gifPlayerRefreshFiles();
    bool replacingExisting = false;
    for (uint8_t i = 0; i < gifPathCount; ++i) {
        const char *storedName = strrchr(gifPaths[i], '/');
        storedName = storedName != nullptr ? storedName + 1 : gifPaths[i];
        if (name.equals(storedName)) {
            replacingExisting = true;
            break;
        }
    }
    if (gifPathCount >= 12 && !replacingExisting) return false;

    LittleFS.mkdir("/gif");
    snprintf(uploadGifPath, sizeof(uploadGifPath), "/gif/%s", name.c_str());
    snprintf(uploadGifTempPath, sizeof(uploadGifTempPath), "/gif/.%s.tmp", name.c_str());
    LittleFS.remove(uploadGifTempPath);
    uploadGifFile = LittleFS.open(uploadGifTempPath, "w");
    uploadGifBytes = 0;
    if (!uploadGifFile) {
        LittleFS.remove(uploadGifTempPath);
        uploadGifPath[0] = '\0';
        uploadGifTempPath[0] = '\0';
        return false;
    }
    return true;
}

bool gifPlayerUploadChunk(const uint8_t *data, size_t length) {
    if (!uploadGifFile || data == nullptr || length == 0) return false;
    if (uploadGifBytes + length > 300UL * 1024UL) return false;
    const size_t written = uploadGifFile.write(data, length);
    uploadGifBytes += written;
    return written == length;
}

bool gifPlayerUploadEnd() {
    if (!uploadGifFile) return false;
    uploadGifFile.close();
    bool valid = uploadGifBytes >= 10 && LittleFS.exists(uploadGifTempPath);
    if (valid) {
        File verify = LittleFS.open(uploadGifTempPath, "r");
        uint8_t header[10] = {0};
        const size_t headerBytes = verify ? verify.read(header, sizeof(header)) : 0;
        if (verify) verify.close();
        const bool gifSignature =
            memcmp(header, "GIF87a", 6) == 0 || memcmp(header, "GIF89a", 6) == 0;
        const uint16_t width = static_cast<uint16_t>(header[6] | (header[7] << 8));
        const uint16_t height = static_cast<uint16_t>(header[8] | (header[9] << 8));
        valid = headerBytes == sizeof(header) && gifSignature &&
                width > 0 && width <= kDisplayWidth &&
                height > 0 && height <= kDisplayHeight;
    }
    String backupPath = String(uploadGifPath) + ".bak";
    if (valid) {
        LittleFS.remove(backupPath);
        if (LittleFS.exists(uploadGifPath) && !LittleFS.rename(uploadGifPath, backupPath)) {
            valid = false;
        }
        if (valid && !LittleFS.rename(uploadGifTempPath, uploadGifPath)) {
            valid = false;
        }
        if (valid) LittleFS.remove(backupPath);
        else if (LittleFS.exists(backupPath)) LittleFS.rename(backupPath, uploadGifPath);
    }
    if (!valid) LittleFS.remove(uploadGifTempPath);
    uploadGifPath[0] = '\0';
    uploadGifTempPath[0] = '\0';
    uploadGifBytes = 0;
    gifFileListDirty = true;
    gifPlayerRefreshFiles();
    return valid;
}

bool gifPlayerUploadAbort() {
    if (uploadGifFile) uploadGifFile.close();
    if (uploadGifTempPath[0] != '\0') LittleFS.remove(uploadGifTempPath);
    uploadGifPath[0] = '\0';
    uploadGifTempPath[0] = '\0';
    uploadGifBytes = 0;
    gifFileListDirty = true;
    return true;
}
