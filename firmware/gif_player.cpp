#include "gif_player.h"

#include <LittleFS.h>
#include <ESP8266WiFi.h>
#include <new>
#include <string.h>
#include <AnimatedGIF.h>

namespace {
constexpr int kDisplayWidth = 240;
constexpr int kDisplayHeight = 240;
constexpr uint32_t kHeapSafetyMargin = 8192;

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
uint8_t currentGifIndex = 0;
bool rejectedGifPaths[12] = {false};
int16_t canvasOriginX = 0;
int16_t canvasOriginY = 0;
int16_t canvasWidth = 0;
int16_t canvasHeight = 0;
bool unsupportedFrame = false;
bool fallbackAnimationActive = false;
uint32_t fallbackFrameAtMs = 0;
constexpr int16_t kGifViewportWidth = 104;
constexpr int16_t kGifViewportHeight = 104;
float gifScale = 1.0f;
int16_t scaledCanvasWidth = 0;
int16_t scaledCanvasHeight = 0;

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

uint16_t toPhosphor(uint16_t source) {
    const uint16_t r = static_cast<uint16_t>(((source >> 11) & 0x1F) * 255U / 31U);
    const uint16_t g = static_cast<uint16_t>(((source >> 5) & 0x3F) * 255U / 63U);
    const uint16_t b = static_cast<uint16_t>((source & 0x1F) * 255U / 31U);
    const uint16_t lum = static_cast<uint16_t>((r * 77U + g * 150U + b * 29U) >> 8);
    return static_cast<uint16_t>(((lum * 63U + 127U) / 255U) << 5);
}

void drawGifScanline(GIFDRAW *line) {
    if (line == nullptr || targetDisplay == nullptr || line->pPixels == nullptr ||
        line->pPalette == nullptr || unsupportedFrame) return;

    // The library's no-framebuffer callback path does not restore disposal
    // method 2. Clear the previous frame's rectangle when the next frame starts.
    if (line->y == 0) {
        // This low-RAM scanline renderer has no compositing framebuffer.
        // Accept only full-canvas, opaque frames; partial or transparent frames
        // would otherwise leave pixels from the previous frame visible.
        if (line->iX != 0 || line->iY != 0 ||
            line->iWidth != canvasWidth || line->iHeight != canvasHeight ||
            line->ucHasTransparency) {
            unsupportedFrame = true;
            return;
        }
    }

    // Decode into one small destination scanline, then send contiguous runs
    // to the TFT in bulk. Per-pixel fillRect() calls made animation far too slow.
    const int16_t sourceY = static_cast<int16_t>(line->iY + line->y);
    if (sourceY < 0 || sourceY >= canvasHeight) return;

    const int16_t dy0 = static_cast<int16_t>(canvasOriginY +
        static_cast<int16_t>(sourceY * gifScale));
    const int16_t dy1 = static_cast<int16_t>(canvasOriginY +
        static_cast<int16_t>((sourceY + 1) * gifScale));
    if (dy1 <= dy0) return;

    bool dirty[104] = {false};
    uint16_t row[104] = {0};
    for (int pixel = 0; pixel < line->iWidth; ++pixel) {
        const int16_t sx = static_cast<int16_t>(line->iX + pixel);
        if (sx < 0 || sx >= canvasWidth) continue;

        const uint8_t index = line->pPixels[pixel];
        if (line->ucHasTransparency && index == line->ucTransparent) continue;

        const uint16_t phosphor = toPhosphor(line->pPalette[index]);

        const int16_t dx0 = static_cast<int16_t>(canvasOriginX +
            static_cast<int16_t>(sx * gifScale));
        const int16_t dx1 = static_cast<int16_t>(canvasOriginX +
            static_cast<int16_t>((sx + 1) * gifScale));
        const int16_t left = dx0 > canvasOriginX ? dx0 : canvasOriginX;
        const int16_t right = dx1 < canvasOriginX + scaledCanvasWidth
            ? dx1 : canvasOriginX + scaledCanvasWidth;
        for (int16_t dx = left; dx < right; ++dx) {
            const int16_t offset = static_cast<int16_t>(dx - canvasOriginX);
            if (offset >= 0 && offset < 104) {
                row[offset] = phosphor;
                dirty[offset] = true;
            }
        }
    }

    const int16_t top = dy0 > 0 ? dy0 : 0;
    const int16_t bottom = dy1 < kDisplayHeight ? dy1 : kDisplayHeight;
    for (int16_t y = top; y < bottom; ++y) {
        int16_t x = 0;
        while (x < scaledCanvasWidth) {
            while (x < scaledCanvasWidth && !dirty[x]) ++x;
            const int16_t runStart = x;
            while (x < scaledCanvasWidth && dirty[x]) ++x;
            if (x > runStart) {
                targetDisplay->pushImage(canvasOriginX + runStart, y,
                    static_cast<uint16_t>(x - runStart), 1, &row[runStart]);
            }
        }
    }
    yield();
}
}  // namespace

bool gifPlayerStart(const char *path, TFT_eSPI &display) {
    gifPlayerStop();
    if (path == nullptr || path[0] != '/') return false;

    // A generic GIF needs the complete 12-bit LZW dictionary. That decoder
    // no longer fits the ESP8266's small IRAM heap, so use the normal heap,
    // but only when enough free heap remains for Wi-Fi and the web server.
    const uint32_t heapFree = ESP.getFreeHeap();
    const size_t required = sizeof(AnimatedGIF) + kHeapSafetyMargin;
    if (heapFree < required) {
        Serial.printf("GIF skipped: heap free=%u need=%u\\n",
                      static_cast<unsigned int>(heapFree),
                      static_cast<unsigned int>(required));
        return false;
    }

    decoder = new (std::nothrow) AnimatedGIF();
    if (decoder == nullptr) {
        Serial.println(F("GIF skipped: decoder allocation failed"));
        return false;
    }

    targetDisplay = &display;
    decoder->begin(GIF_PALETTE_RGB565_LE);
    if (!decoder->open(path, openGifFile, closeGifFile, readGifFile, seekGifFile, drawGifScanline)) {
        Serial.printf("GIF skipped: decoder open failed (%d)\n", decoder->getLastError());
        gifPlayerStop();
        return false;
    }

    canvasWidth = static_cast<int16_t>(decoder->getCanvasWidth());
    canvasHeight = static_cast<int16_t>(decoder->getCanvasHeight());
    if (canvasWidth <= 0 || canvasHeight <= 0 ||
        canvasWidth > kDisplayWidth || canvasHeight > kDisplayHeight) {
        Serial.println(F("GIF skipped: invalid canvas dimensions"));
        gifPlayerStop();
        return false;
    }
    const float sx = static_cast<float>(kGifViewportWidth) / canvasWidth;
    const float sy = static_cast<float>(kGifViewportHeight) / canvasHeight;
    gifScale = sx < sy ? sx : sy;
    scaledCanvasWidth = static_cast<int16_t>(canvasWidth * gifScale);
    if (scaledCanvasWidth < 1) scaledCanvasWidth = 1;
    scaledCanvasHeight = static_cast<int16_t>(canvasHeight * gifScale);
    if (scaledCanvasHeight < 1) scaledCanvasHeight = 1;
    canvasOriginX = static_cast<int16_t>((kDisplayWidth - scaledCanvasWidth) / 2);
    canvasOriginY = static_cast<int16_t>(76 + (104 - scaledCanvasHeight) / 2);
    unsupportedFrame = false;
    nextFrameAtMs = 0;
    gifStartedAtMs = millis();
    return true;
}

bool gifPlayerTick(uint32_t nowMs) {
    if (fallbackAnimationActive && decoder == nullptr && targetDisplay != nullptr) {
        // Do not let one damaged or unsupported album entry pin RADIO forever.
        // Rotate after the same 20-second dwell used for valid GIFs.
        if (nowMs - gifStartedAtMs >= 20000UL) {
            TFT_eSPI *display = targetDisplay;
            gifPlayerStop();
            if (display != nullptr) gifPlayerStartNext(*display);
            return true;
        }
        if (static_cast<int32_t>(nowMs - fallbackFrameAtMs) < 0) return false;
        fallbackFrameAtMs = nowMs + 110UL;
        TFT_eSPI &display = *targetDisplay;
        const uint16_t phosphor = 0x07E0;
        const uint16_t dim = 0x03E0;
        const uint16_t pale = 0xAFE5;
        const bool blink = ((nowMs / 110UL) % 19UL) == 0;
        const int scanY = 87 + static_cast<int>((nowMs / 45UL) % 78UL);
        // Fallback artwork uses the same compact 104x104 viewport as uploaded GIFs.
        display.fillRect(68, 76, 104, 104, TFT_BLACK);
        display.drawRect(68, 76, 104, 104, dim);
        display.drawRoundRect(99, 84, 42, 78, 9, dim);
        display.fillRoundRect(102, 87, 36, 72, 8, 0x0100);
        display.drawFastHLine(106, 93, 28, phosphor);
        display.drawRect(106, 99, 28, 7, dim);
        display.fillRoundRect(106, 110, 28, 23, 4, dim);
        display.drawRoundRect(106, 110, 28, 23, 4, phosphor);
        display.fillRect(110, 117, 8, blink ? 2 : 5, blink ? dim : pale);
        display.fillRect(122, 117, 8, blink ? 2 : 5, blink ? dim : pale);
        display.drawFastHLine(111, 139, 18, phosphor);
        display.drawLine(114, 142, 120, 149, dim);
        display.drawLine(126, 142, 120, 149, dim);
        display.fillRoundRect(90, 113, 8, 30, 3, 0x0100);
        display.drawRoundRect(90, 113, 8, 30, 3, phosphor);
        display.fillRoundRect(142, 113, 8, 30, 3, 0x0100);
        display.drawRoundRect(142, 113, 8, 30, 3, phosphor);
        display.drawCircle(94, 128, 2, pale);
        display.drawCircle(146, 128, 2, pale);
        display.drawFastHLine(72, scanY, 96, dim);
        display.setTextDatum(TC_DATUM);
        display.setTextFont(1);
        display.setTextColor(phosphor, TFT_BLACK);
        display.drawString("ROBCO // ARCHIVE", 120, 78, 1);
        display.setTextColor(pale, TFT_BLACK);
        display.drawString("PIP-BOY", 120, 165, 1);
        yield();
        return true;
    }
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
        Serial.printf("GIF skipped: frame decode failed (%d), unsupported=%u\n",
                      result, unsupportedFrame ? 1U : 0U);
        TFT_eSPI *display = targetDisplay;
        gifPlayerStop();
        if (display != nullptr) {
            targetDisplay = display;
            fallbackAnimationActive = true;
            fallbackFrameAtMs = 0;
        }
        return false;
    }

    // AnimatedGIF reports 0 after the final frame. Rewind immediately so
    // trailer bytes are never mistaken for another frame on the next tick.
    if (result == 0) decoder->reset();

    if (delayMs < 20) delayMs = 20;
    if (delayMs > 5000) delayMs = 5000;
    nextFrameAtMs = nowMs + static_cast<uint32_t>(delayMs);
    yield();
    return true;
}

void gifPlayerStop() {
    if (decoder != nullptr) {
        decoder->close();
        delete decoder;
        decoder = nullptr;
    }
    if (activeGifFile) activeGifFile.close();
    targetDisplay = nullptr;
    fallbackAnimationActive = false;
    fallbackFrameAtMs = 0;
    nextFrameAtMs = 0;
    gifStartedAtMs = 0;
    canvasOriginX = 0;
    canvasOriginY = 0;
    canvasWidth = 0;
    canvasHeight = 0;
    gifScale = 1.0f;
    scaledCanvasWidth = 0;
    scaledCanvasHeight = 0;
    unsupportedFrame = false;
}

bool gifPlayerIsActive() {
    return decoder != nullptr || fallbackAnimationActive;
}

size_t gifPlayerDecoderBytes() {
    return sizeof(AnimatedGIF);
}


bool gifPlayerRefreshFiles() {
    gifPathCount = 0;
    memset(rejectedGifPaths, 0, sizeof(rejectedGifPaths));
    const char *directories[] = {"/gif", "/image"};
    for (uint8_t directoryIndex = 0; directoryIndex < 2 && gifPathCount < 12; ++directoryIndex) {
        Dir dir = LittleFS.openDir(directories[directoryIndex]);
        while (dir.next() && gifPathCount < 12) {
            String name = dir.fileName();
            if (!name.endsWith(".gif") && !name.endsWith(".GIF")) continue;
            if (dir.fileSize() == 0 || dir.fileSize() > 300UL * 1024UL) continue;

            String path = name.startsWith("/") ? name : String(directories[directoryIndex]) + "/" + name;
            if (path.length() >= sizeof(gifPaths[0])) continue;
            path.toCharArray(gifPaths[gifPathCount], sizeof(gifPaths[0]));
            ++gifPathCount;
        }
    }

    // Preserve the stock firmware's /image album when the filesystem survives
    // the firmware replacement; also include newly uploaded /gif entries.
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

    for (uint8_t attempt = 0; attempt < gifPathCount; ++attempt) {
        const uint8_t selected = nextGifIndex;
        nextGifIndex = static_cast<uint8_t>((nextGifIndex + 1) % gifPathCount);
        if (rejectedGifPaths[selected]) continue;
        if (gifPlayerStart(gifPaths[selected], display)) {
            currentGifIndex = selected;
            return true;
        }
        rejectedGifPaths[selected] = true;
    }

    // Every entry was rejected or could not be opened. Retry only on the next
    // explicit RADIO entry or after the archive is refreshed.
    memset(rejectedGifPaths, 0, sizeof(rejectedGifPaths));
    return false;
}

bool gifPlayerUploadStart(const char *filename) {
    gifPlayerStop();
    if (filename == nullptr || filename[0] == '\0') return false;

    String name(filename);
    int slash = max(name.lastIndexOf('/'), name.lastIndexOf('\\'));
    if (slash >= 0) name = name.substring(slash + 1);
    if (name.length() == 0 || name.length() > 31 ||
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
    // LittleFS limits each path component to 31 bytes. A valid final GIF name
    // may exceed that limit when decorated with a temporary-file suffix.
    // Uploads are serialized by the synchronous web server, so fixed staging
    // names are safe and keep the temporary component short.
    strlcpy(uploadGifTempPath, "/gif/.upload.tmp", sizeof(uploadGifTempPath));
    LittleFS.remove(uploadGifTempPath);
    LittleFS.remove("/gif/.previous.bak");
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

    // Keep a small LittleFS reserve for metadata and safe file finalization.
    // The previous file remains in place until the temporary upload is complete,
    // so free space is checked against the actual current filesystem usage.
    FSInfo filesystemInfo;
    if (!LittleFS.info(filesystemInfo) ||
        filesystemInfo.usedBytes >= filesystemInfo.totalBytes) return false;
    const size_t freeBytes = filesystemInfo.totalBytes - filesystemInfo.usedBytes;
    constexpr size_t kFilesystemReserve = 4096;
    if (length > freeBytes || freeBytes - length < kFilesystemReserve) return false;

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
    const char *backupPath = "/gif/.previous.bak";
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
