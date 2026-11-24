#!/usr/bin/env python3
"""Improve SmallTV readability and add a stable built-in Pip-Boy animation."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
display_cpp = root / "src/display.cpp"
gif_cpp = root / "src/gif_player.cpp"

def replace_function(source: str, signature: str, next_signature: str, replacement: str) -> str:
    start = source.index(signature)
    end = source.index(next_signature, start)
    return source[:start] + replacement.rstrip() + "\n\n" + source[end:]

s = display_cpp.read_text(encoding="utf-8")

weather = r'''void renderWeatherPage() {
    const ThemePalette &theme = activeTheme();
    drawScreenChrome("DATA // WASTELAND WEATHER");

    if (!hasWeatherContent()) {
        tft.drawRect(10, 72, 220, 125, theme.accent);
        drawDisplayLabel("METEOROLOGICAL DATABASE", 120, 82, 204,
                         TC_DATUM, theme.accent, FONT_LABEL);
        if (feedRuntime.weather.lastError[0] != '\0') {
            drawDisplayLabel("WEATHER LINK // ERROR", 120, 119, 204,
                             TC_DATUM, theme.warning, FONT_LABEL);
            drawDisplayLabel(feedRuntime.weather.lastError, 120, 145, 204,
                             TC_DATUM, theme.text, FONT_LABEL);
        } else {
            drawDisplayLabel(feedRuntime.weather.syncing ? "ESTABLISHING DATA LINK"
                                                         : "NO WEATHER DATA RECEIVED",
                             120, 132, 204, TC_DATUM, theme.text, FONT_LABEL);
        }
        return;
    }

    const WeatherData *weather = effectiveWeatherData();

    // Location and current condition occupy a clear, high-contrast hero panel.
    tft.drawRect(8, 68, 224, 82, theme.accent);
    tft.drawRect(11, 71, 218, 76, theme.accentSoft);
    drawDisplayLabel(weather->location[0] != '\0' ? weather->location : "LOCAL WEATHER",
                     120, 75, 208, TC_DATUM, theme.muted, FONT_LABEL);

    const String currentTemp = formatWeatherTemperature(weather->temperature);
    drawHeroText(currentTemp, 88, 45, theme.text, 2);
    drawDisplayLabel(weather->condition[0] != '\0' ? weather->condition : "CURRENT CONDITIONS",
                     120, 132, 208, TC_DATUM, theme.accent, FONT_LABEL);

    drawDisplayLabel("FORECAST // NEXT 3 DAYS", 10, 153, 220,
                     TL_DATUM, theme.accent, FONT_LABEL);
    tft.drawFastHLine(10, 169, 220, theme.accentSoft);

    // Three full-width rows are substantially more legible than tiny cards.
    for (uint8_t slot = 0; slot < 3; ++slot) {
        const int y = 170 + static_cast<int>(slot) * 16;
        if (slot > 0) tft.drawFastHLine(10, y - 2, 220, theme.surface);
        if (weather->forecastCount > slot + 1) {
            const WeatherForecastDay &day = weather->forecast[slot + 1];
            drawDisplayLabel(day.date, 12, y, 48, TL_DATUM, theme.text, FONT_LABEL);
            String range = String(day.high) + "/" + String(day.low) + "C";
            drawDisplayLabel(range, 120, y, 82, TC_DATUM, theme.text, FONT_INFO);
            drawDisplayLabel(String(day.rainChance) + "%", 228, y, 44,
                             TR_DATUM, theme.accent, FONT_LABEL);
        } else {
            drawDisplayLabel("--", 12, y, 48, TL_DATUM, theme.muted, FONT_LABEL);
            drawDisplayLabel("--/--", 120, y, 82, TC_DATUM, theme.muted, FONT_LABEL);
            drawDisplayLabel("--", 228, y, 44, TR_DATUM, theme.muted, FONT_LABEL);
        }
    }
}'''
s = replace_function(s, "void renderWeatherPage() {", "void renderMarketsPage() {", weather)

# Replace the stock brightness-only page fade with a short RobCo scan transition.
transition = r'''void playPipboyTransition() {
    const uint16_t phosphor = 0x07E0;
    const uint16_t dim = 0x03E0;
    tft.fillScreen(TFT_BLACK);
    tft.setTextDatum(TC_DATUM);
    tft.setTextFont(FONT_LABEL);
    tft.setTextColor(phosphor, TFT_BLACK);
    tft.drawString("ROBCO INDUSTRIES", 120, 82, FONT_LABEL);
    tft.setTextFont(FONT_INFO);
    tft.setTextColor(dim, TFT_BLACK);
    tft.drawString("PIP-OS // LOADING MODULE", 120, 105, FONT_INFO);
    tft.drawRect(30, 137, 180, 12, dim);
    for (uint8_t step = 0; step < 6; ++step) {
        tft.fillRect(33, 140, 174, 6, TFT_BLACK);
        tft.fillRect(33, 140, 29 * (step + 1), 6, phosphor);
        const int scanY = 158 + step * 4;
        tft.drawFastHLine(24, scanY, 192, dim);
        delay(22);
        yield();
    }
}'''
needle = "void displayCycleNextPage(bool smoothTransition) {"
if needle not in s:
    raise SystemExit("Could not locate displayCycleNextPage")
if "void playPipboyTransition()" not in s:
    s = s.replace(needle, transition + "\n\n" + needle, 1)
needle = "    int targetBrightness = appliedBrightness;"
if needle not in s:
    raise SystemExit("Could not locate page transition brightness block")
s = s.replace(needle, "    if (smoothTransition) playPipboyTransition();\n\n" + needle, 1)

# Move the common footer down so the larger forecast rows have room.
s = s.replace("tft.drawFastHLine(8, 207, 224, theme.accent);", "tft.drawFastHLine(8, 223, 224, theme.accent);")
s = s.replace("tft.drawFastHLine(8, 209, 224, theme.accentSoft);", "tft.drawFastHLine(8, 225, 224, theme.accentSoft);")
s = s.replace('''drawDisplayLabel("VAULT-TEC // PERSONNEL DEVICE", 232, 219, 128,''', '''drawDisplayLabel("VAULT-TEC // PERSONNEL DEVICE", 232, 230, 128,''')

display_cpp.write_text(s, encoding="utf-8")

# Add a built-in animated Pip-Boy terminal scene when the old stock GIF album
# was not migrated into the new LittleFS filesystem. Only small moving regions
# are redrawn, avoiding the full-screen flash of the first prototype.
s = gif_cpp.read_text(encoding="utf-8")
needle = "uint8_t nextGifIndex = 0;"
if needle not in s:
    raise SystemExit("Could not locate GIF index state")
if "bool fallbackAnimationActive = false;" not in s:
    s = s.replace(needle, needle + "\nbool fallbackAnimationActive = false;\nbool fallbackSceneDrawn = false;\nuint32_t fallbackFrameAtMs = 0;\nint16_t fallbackScanY = 0;", 1)

tick = r'''bool gifPlayerTick(uint32_t nowMs) {
    if (fallbackAnimationActive && decoder == nullptr && targetDisplay != nullptr) {
        TFT_eSPI &display = *targetDisplay;
        if (!fallbackSceneDrawn) {
            display.fillRect(12, 61, 216, 142, TFT_BLACK);
            display.drawRoundRect(70, 72, 100, 116, 17, 0x03E0);
            display.drawRoundRect(75, 77, 90, 106, 14, 0x07E0);
            display.drawFastHLine(87, 88, 66, 0x07E0);
            display.drawRect(87, 96, 66, 12, 0x03E0);
            display.drawRoundRect(88, 113, 64, 34, 7, 0x07E0);
            display.drawFastHLine(99, 155, 42, 0x07E0);
            display.drawLine(105, 160, 120, 170, 0x03E0);
            display.drawLine(135, 160, 120, 170, 0x03E0);
            display.drawRoundRect(52, 115, 18, 42, 5, 0x03E0);
            display.drawRoundRect(170, 115, 18, 42, 5, 0x03E0);
            display.drawCircle(61, 136, 3, 0xAFE5);
            display.drawCircle(179, 136, 3, 0xAFE5);
            display.setTextDatum(TC_DATUM);
            display.setTextFont(1);
            display.setTextColor(0x07E0, TFT_BLACK);
            display.drawString("ROBCO // VISUAL ARCHIVE", 120, 63, 1);
            display.setTextColor(0xAFE5, TFT_BLACK);
            display.drawString("SYSTEM ANIMATION", 120, 191, 1);
            display.setTextColor(0x03E0, TFT_BLACK);
            display.drawString("PIP-OS 3000 // MK IV", 120, 212, 1);
            fallbackScanY = 114;
            fallbackSceneDrawn = true;
            fallbackFrameAtMs = nowMs;
        }

        if (static_cast<uint32_t>(nowMs - fallbackFrameAtMs) < 85UL) return false;
        fallbackFrameAtMs = nowMs;
        display.drawFastHLine(91, fallbackScanY, 58, TFT_BLACK);
        fallbackScanY += 3;
        if (fallbackScanY > 145) fallbackScanY = 114;
        display.drawFastHLine(91, fallbackScanY, 58, 0x5FEC);
        display.fillRect(95, 122, 8, 3, 0xAFE5);
        display.fillRect(137, 122, 8, 3, 0xAFE5);
        display.drawPixel(120, 176, ((nowMs / 400UL) & 1U) ? 0x07E0 : 0x03E0);
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
            fallbackSceneDrawn = false;
        }
        return false;
    }

    if (result == 0) decoder->reset();
    if (delayMs < 20) delayMs = 20;
    if (delayMs > 5000) delayMs = 5000;
    nextFrameAtMs = nowMs + static_cast<uint32_t>(delayMs);
    yield();
    return true;
}'''
s = replace_function(s, "bool gifPlayerTick(uint32_t nowMs) {", "void gifPlayerStop() {", tick)

# Ensure stop/status/start paths correctly track the built-in animation.
s = s.replace("    targetDisplay = nullptr;\n    nextFrameAtMs = 0;", "    targetDisplay = nullptr;\n    fallbackAnimationActive = false;\n    fallbackSceneDrawn = false;\n    fallbackFrameAtMs = 0;\n    nextFrameAtMs = 0;", 1)
s = s.replace("    return decoder != nullptr;", "    return decoder != nullptr || fallbackAnimationActive;", 1)

start_next = r'''bool gifPlayerStartNext(TFT_eSPI &display) {
    if (gifFileListDirty) gifPlayerRefreshFiles();
    if (gifPathCount == 0) {
        targetDisplay = &display;
        fallbackAnimationActive = true;
        fallbackSceneDrawn = false;
        fallbackFrameAtMs = 0;
        return true;
    }

    const uint8_t selected = nextGifIndex;
    nextGifIndex = static_cast<uint8_t>((nextGifIndex + 1) % gifPathCount);
    if (gifPlayerStart(gifPaths[selected], display)) return true;

    targetDisplay = &display;
    fallbackAnimationActive = true;
    fallbackSceneDrawn = false;
    fallbackFrameAtMs = 0;
    return true;
}'''
s = replace_function(s, "bool gifPlayerStartNext(TFT_eSPI &display) {", "bool gifPlayerUploadStart(", start_next)

gif_cpp.write_text(s, encoding="utf-8")
print("Readable weather page, RobCo page transition and non-flashing built-in animation applied")
