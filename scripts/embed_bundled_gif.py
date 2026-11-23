#!/usr/bin/env python3
"""Embed the verified GIF in the application image and seed it into LittleFS at boot."""
from pathlib import Path
import sys
import zlib
from PIL import Image

if len(sys.argv) != 3:
    raise SystemExit("usage: embed_bundled_gif.py <firmware-root> <compatible-gif>")

root = Path(sys.argv[1])
gif_path = Path(sys.argv[2])
data = gif_path.read_bytes()
if len(data) < 32 or len(data) > 300 * 1024 or data[:3] != b"GIF":
    raise SystemExit("Bundled GIF is missing, invalid, or outside the 300 KiB limit")

crc = zlib.crc32(data) & 0xFFFFFFFF
frames = []
durations = []
with Image.open(gif_path) as animation:
    if animation.size != (104, 104) or animation.n_frames < 2 or animation.n_frames > 36:
        raise SystemExit("Bundled animation must contain 2..36 frames at 104x104")
    for index in range(animation.n_frames):
        animation.seek(index)
        rgb = animation.convert("RGB")
        # Store original artwork colors as RGB565 for heap-free playback.
        pixels = []
        for red, green, blue in rgb.getdata():
            value = ((red >> 3) << 11) | ((green >> 2) << 5) | (blue >> 3)
            pixels.append(value)
        frames.append(tuple(pixels))
        durations.append(max(40, min(1000, int(animation.info.get("duration", 100)))))
if len(set(frames)) < 2:
    raise SystemExit("Bundled animation contains fewer than two unique frames")

header = root / "src" / "bundled_gif.h"
rows = []
for offset in range(0, len(data), 16):
    rows.append("    " + ", ".join(f"0x{value:02X}" for value in data[offset:offset + 16]) + ",")
frame_rows = []
for frame in frames:
    frame_rows.append("    {\n" + "\n".join(
        "        " + ", ".join(f"0x{value:04X}" for value in frame[offset:offset + 8]) + ","
        for offset in range(0, len(frame), 8)
    ) + "\n    },")
header.write_text(
    "#pragma once\n"
    "#include <Arduino.h>\n"
    "#include <pgmspace.h>\n\n"
    "static const uint8_t kBundledVaultBoyGif[] PROGMEM = {\n"
    + "\n".join(rows)
    + "\n};\n"
    + f"static const uint32_t kBundledVaultBoyGifCrc32 = 0x{crc:08X}UL;\n"
    + f"static const uint8_t kBundledVaultBoyFrameCount = {len(frames)};\n"
    + "static const uint16_t kBundledVaultBoyFrameDurationMs[] PROGMEM = {"
    + ", ".join(str(value) for value in durations) + "};\n"
    + "static const uint16_t kBundledVaultBoyFrames[][104 * 104] PROGMEM = {\n"
    + "\n".join(frame_rows)
    + "\n};\n",
    encoding="utf-8",
)

player_h = root / "src" / "gif_player.h"
h = player_h.read_text(encoding="utf-8")
declaration = "bool gifPlayerInstallBundledAsset();"
if declaration not in h:
    anchor = "bool gifPlayerRefreshFiles();"
    if anchor not in h:
        raise SystemExit("gif_player.h API anchor not found")
    h = h.replace(anchor, declaration + "\n" + anchor, 1)
player_h.write_text(h, encoding="utf-8")

player_cpp = root / "src" / "gif_player.cpp"
s = player_cpp.read_text(encoding="utf-8")
if '#include "bundled_gif.h"' not in s:
    anchor = "#include <AnimatedGIF.h>"
    if anchor not in s:
        raise SystemExit("gif_player.cpp include anchor not found")
    s = s.replace(anchor, anchor + '\n#include "bundled_gif.h"', 1)

function = r'''
namespace {
uint32_t bundledFileCrc32(File &file) {
    uint32_t crc = 0xFFFFFFFFUL;
    uint8_t buffer[128];
    while (file.available()) {
        const size_t count = file.read(buffer, sizeof(buffer));
        if (count == 0) break;
        for (size_t i = 0; i < count; ++i) {
            crc ^= buffer[i];
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ ((crc & 1U) ? 0xEDB88320UL : 0UL);
            }
        }
    }
    return crc ^ 0xFFFFFFFFUL;
}
}

bool gifPlayerInstallBundledAsset() {
    static const char *kPath = "/gif/bethesda-vaultboy.gif";
    LittleFS.mkdir("/gif");

    File existing = LittleFS.open(kPath, "r");
    if (existing) {
        const bool sameSize = existing.size() == sizeof(kBundledVaultBoyGif);
        const bool sameContent = sameSize &&
            bundledFileCrc32(existing) == kBundledVaultBoyGifCrc32;
        existing.close();
        if (sameContent) {
            gifFileListDirty = true;
            return gifPlayerRefreshFiles();
        }
    }

    LittleFS.remove(kPath);
    File output = LittleFS.open(kPath, "w");
    if (!output) {
        Serial.println(F("Bundled GIF install failed: cannot open LittleFS file"));
        return false;
    }

    uint8_t buffer[128];
    size_t offset = 0;
    bool writeOk = true;
    while (offset < sizeof(kBundledVaultBoyGif)) {
        const size_t count = (sizeof(kBundledVaultBoyGif) - offset) < sizeof(buffer)
            ? (sizeof(kBundledVaultBoyGif) - offset) : sizeof(buffer);
        for (size_t i = 0; i < count; ++i) {
            buffer[i] = pgm_read_byte(kBundledVaultBoyGif + offset + i);
        }
        if (output.write(buffer, count) != count) {
            writeOk = false;
            break;
        }
        offset += count;
        yield();
    }
    output.flush();
    output.close();

    if (!writeOk || offset != sizeof(kBundledVaultBoyGif)) {
        LittleFS.remove(kPath);
        Serial.println(F("Bundled GIF install failed: incomplete LittleFS write"));
        return false;
    }

    File verify = LittleFS.open(kPath, "r");
    const bool verified = verify &&
        verify.size() == sizeof(kBundledVaultBoyGif) &&
        bundledFileCrc32(verify) == kBundledVaultBoyGifCrc32;
    if (verify) verify.close();
    if (!verified) {
        LittleFS.remove(kPath);
        Serial.println(F("Bundled GIF install failed: read-back CRC mismatch"));
        return false;
    }

    gifFileListDirty = true;
    Serial.printf("Bundled GIF installed and verified: %u bytes, CRC32 %08lx\n",
                  static_cast<unsigned int>(sizeof(kBundledVaultBoyGif)),
                  static_cast<unsigned long>(kBundledVaultBoyGifCrc32));
    return gifPlayerRefreshFiles();
}
'''
if "bool gifPlayerInstallBundledAsset()" not in s:
    anchor = "bool gifPlayerRefreshFiles() {"
    if anchor not in s:
        raise SystemExit("gif_player.cpp refresh anchor not found")
    s = s.replace(anchor, function + "\n" + anchor, 1)
if "bool bundledAnimationActive = false;" not in s:
    anchor = "bool fallbackAnimationActive = false;"
    if anchor not in s:
        raise SystemExit("GIF player fallback state anchor not found")
    s = s.replace(anchor, anchor + "\nbool bundledAnimationActive = false;\nuint8_t bundledFrameIndex = 0;", 1)

if "if(bundledAnimationActive && decoder==nullptr && targetDisplay!=nullptr)" not in s:
    anchor = "    if(decoder==nullptr)return false;"
    if anchor not in s:
        raise SystemExit("GIF player tick insertion anchor not found")
    bundled_tick = r'''
    if(bundledAnimationActive && decoder==nullptr && targetDisplay!=nullptr) {
        if(nowMs-gifStartedAtMs>=20000UL) {
            TFT_eSPI *d=targetDisplay; gifPlayerStop(); if(d) gifPlayerStartNext(*d); return true;
        }
        if(static_cast<int32_t>(nowMs-nextFrameAtMs)<0)return false;
        const uint8_t frameIndex = bundledFrameIndex;
        const uint8_t *frame = kBundledVaultBoyFrames[frameIndex];
        uint16_t row[104];
        for(int16_t y=0;y<104;++y) {
            for(int16_t x=0;x<104;++x) {
                row[x] = pgm_read_word(frame + y*104 + x);
            }
            targetDisplay->pushImage(68,76+y,104,1,row);
        }
        uint16_t delayMs = pgm_read_word(&kBundledVaultBoyFrameDurationMs[frameIndex]);
        if(delayMs<40)delayMs=40;
        if(delayMs>1000)delayMs=1000;
        bundledFrameIndex = static_cast<uint8_t>((frameIndex+1U)%kBundledVaultBoyFrameCount);
        nextFrameAtMs = nowMs + delayMs;
        yield(); return true;
    }
'''
    s = s.replace(anchor, bundled_tick + anchor, 1)

if "strcmp(gifPaths[selected], \"/gif/bethesda-vaultboy.gif\")" not in s:
    anchor = "        if(rejectedGifPaths[selected])continue;"
    if anchor not in s:
        raise SystemExit("GIF archive selection anchor not found")
    bundled_start = r'''
        if(strcmp(gifPaths[selected], "/gif/bethesda-vaultboy.gif")==0) {
            targetDisplay=&display;
            bundledAnimationActive=true;
            bundledFrameIndex=0;
            nextFrameAtMs=0;
            gifStartedAtMs=millis();
            currentGifIndex=selected;
            Serial.println(F("Bundled Vault Boy sprite animation started"));
            return true;
        }
'''
    s = s.replace(anchor, anchor + bundled_start, 1)

if "bundledAnimationActive = false;" not in s[s.index("void gifPlayerStop()"):s.index("bool gifPlayerIsActive()")]:
    anchor = "    fallbackAnimationActive = false;"
    stop_start = s.index("void gifPlayerStop()")
    stop_end = s.index("bool gifPlayerIsActive()", stop_start)
    part = s[stop_start:stop_end]
    if anchor not in part:
        raise SystemExit("GIF player stop reset anchor not found")
    part = part.replace(anchor, anchor + "\n    bundledAnimationActive = false;\n    bundledFrameIndex = 0;", 1)
    s = s[:stop_start] + part + s[stop_end:]

s=s.replace("return decoder != nullptr || fallbackAnimationActive;","return decoder != nullptr || fallbackAnimationActive || bundledAnimationActive;",1)

player_cpp.write_text(s, encoding="utf-8")

main = root / "src" / "main.cpp"
m = main.read_text(encoding="utf-8")
call = "        if (!gifPlayerInstallBundledAsset()) {\n            Serial.println(F(\"Bundled RADIO GIF unavailable; archive may be empty\"));\n        }\n"
if "gifPlayerInstallBundledAsset()" not in m:
    anchor = "        setupFilesystem();\n"
    if anchor not in m:
        raise SystemExit("main.cpp filesystem setup anchor not found")
    m = m.replace(anchor, anchor + call, 1)
main.write_text(m, encoding="utf-8")

print(f"Embedded {len(data)} GIF bytes and {len(frames)} predecoded sprite frames into firmware; boot-time LittleFS install and CRC verification enabled.")
