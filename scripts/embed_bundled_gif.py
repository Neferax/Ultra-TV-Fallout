#!/usr/bin/env python3
"""Embed the verified GIF in the application image and seed it into LittleFS at boot."""
from pathlib import Path
import sys
import zlib

if len(sys.argv) != 3:
    raise SystemExit("usage: embed_bundled_gif.py <firmware-root> <compatible-gif>")

root = Path(sys.argv[1])
gif_path = Path(sys.argv[2])
data = gif_path.read_bytes()
if len(data) < 32 or len(data) > 300 * 1024 or data[:3] != b"GIF":
    raise SystemExit("Bundled GIF is missing, invalid, or outside the 300 KiB limit")

crc = zlib.crc32(data) & 0xFFFFFFFF
header = root / "src" / "bundled_gif.h"
rows = []
for offset in range(0, len(data), 16):
    rows.append("    " + ", ".join(f"0x{value:02X}" for value in data[offset:offset + 16]) + ",")
header.write_text(
    "#pragma once\n"
    "#include <Arduino.h>\n"
    "#include <pgmspace.h>\n\n"
    "static const uint8_t kBundledVaultBoyGif[] PROGMEM = {\n"
    + "\n".join(rows)
    + "\n};\n"
    + f"static const uint32_t kBundledVaultBoyGifCrc32 = 0x{crc:08X}UL;\n",
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

print(f"Embedded {len(data)} GIF bytes into firmware (CRC32 {crc:08X}); boot-time LittleFS install and read-back verification enabled.")
