#!/usr/bin/env python3
"""V7: readable weather panels and real GIF playback as page transitions."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
display = root / "src/display.cpp"
gif = root / "src/gif_player.cpp"
main = root / "src/main.cpp"

def replace_function(source: str, signature: str, next_signature: str, replacement: str) -> str:
    start = source.index(signature)
    end = source.index(next_signature, start)
    return source[:start] + replacement.rstrip() + "\n\n" + source[end:]

# The previous transition was only a fake RobCo loading screen. Real GIF
# artwork is now rendered by the GIF decoder after a page change.
s = display.read_text(encoding="utf-8")
s = re.sub(r"void playPipboyTransition\(\) \{.*?\n\}\n\n(?=void displayCycleNextPage)", "", s, count=1, flags=re.S)
s = s.replace("    if (smoothTransition) playPipboyTransition();\n\n", "")
# The footer clock used y=212, colliding with the forecast's final row.
footer = r'''void updateFooterClock() {
    if (displayState.currentPage == DASHBOARD_PAGE_CLOCK && !temporaryMessageVisible()) return;
    String text = footerClockText();
    if (strcmp(footerClockCache, text.c_str()) == 0) return;
    const ThemePalette &theme = activeTheme();
    tft.setTextSize(1);
    tft.fillRect(8, 228, 84, 12, theme.background);
    drawDisplayLabel(text, 8, 229, 84, TL_DATUM, theme.text, FONT_INFO);
    strncpy(footerClockCache, text.c_str(), sizeof(footerClockCache) - 1);
    footerClockCache[sizeof(footerClockCache) - 1] = '\0';
}'''
s = replace_function(s, "void updateFooterClock() {", "void drawScreenChrome(", footer)

clock_weather = r'''void renderClockPage() {
    const ThemePalette &theme = activeTheme();
    drawScreenChrome("STATUS // LOCAL TIME");
    clockMetaCache.valid = false;

    tft.drawRect(8, 68, 224, 80, theme.accent);
    tft.drawRect(11, 71, 218, 74, theme.accentSoft);
    updateClockDynamicArea();

    tft.fillRect(10, 155, 220, 58, theme.surface);
    tft.drawRect(10, 155, 220, 58, theme.accentSoft);
    drawDisplayLabel("WETTER // LIVE-DATEN", 18, 159, 204,
                     TL_DATUM, theme.accent, FONT_INFO);

    if (hasWeatherContent()) {
        const WeatherData *weather = effectiveWeatherData();
        const int temperatureFonts[] = {FONT_BODY, FONT_LABEL};
        drawAdaptiveText(formatWeatherTemperature(weather->temperature), 18, 178, 78,
                         TL_DATUM, temperatureFonts, 2, theme.text, theme.surface);
        drawDisplayLabel(weather->condition[0] != '\\0' ? weather->condition : "AKTUELL",
                         220, 180, 126, TR_DATUM, theme.text, FONT_LABEL);
        drawDisplayLabel(weather->location[0] != '\\0' ? weather->location : "DUISBURG",
                         18, 198, 204, TL_DATUM, theme.muted, FONT_INFO);
    } else if (feedRuntime.weather.syncing || weatherWaitingForSync()) {
        drawDisplayLabel("WETTERDATEN WERDEN GELADEN",
                         120, 181, 204, TC_DATUM, theme.text, FONT_LABEL);
        drawDisplayLabel("OPEN-METEO // VERBINDUNG AKTIV",
                         120, 199, 204, TC_DATUM, theme.muted, FONT_INFO);
    } else if (feedRuntime.weather.lastError[0] != '\\0') {
        drawDisplayLabel("WETTERDATEN NICHT VERFUEGBAR",
                         120, 179, 204, TC_DATUM, theme.warning, FONT_LABEL);
        drawDisplayLabel(feedRuntime.weather.lastError,
                         120, 199, 204, TC_DATUM, theme.text, FONT_INFO);
    } else {
        drawDisplayLabel("KEINE WETTERDATEN",
                         120, 184, 204, TC_DATUM, theme.warning, FONT_LABEL);
    }
    drawDisplayLabel("PIP-BOY 3000 // MK IV", 12, 218, 130,
                     TL_DATUM, theme.accent, FONT_INFO);
}

void renderWeatherPage() {
    const ThemePalette &theme = activeTheme();
    drawScreenChrome("WETTER // REGION 47239");

    if (!hasWeatherContent()) {
        tft.drawRect(9, 66, 222, 132, theme.accent);
        tft.drawFastHLine(13, 89, 214, theme.accentSoft);
        drawDisplayLabel("METEOROLOGISCHE DATENBANK", 120, 74, 208,
                         TC_DATUM, theme.accent, FONT_LABEL);
        if (feedRuntime.weather.syncing || weatherWaitingForSync()) {
            drawDisplayLabel("LIVE-VERBINDUNG WIRD AUFGEBAUT",
                             120, 119, 208, TC_DATUM, theme.text, FONT_LABEL);
            drawDisplayLabel("OPEN-METEO // DUISBURG", 120, 145, 208,
                             TC_DATUM, theme.muted, FONT_INFO);
        } else if (feedRuntime.weather.lastError[0] != '\\0') {
            drawDisplayLabel("DATENVERBINDUNG FEHLGESCHLAGEN",
                             120, 115, 208, TC_DATUM, theme.warning, FONT_LABEL);
            drawDisplayLabel(feedRuntime.weather.lastError, 120, 143, 208,
                             TC_DATUM, theme.text, FONT_INFO);
        } else {
            drawDisplayLabel("KEINE WETTERDATEN EMPFANGEN",
                             120, 124, 208, TC_DATUM, theme.warning, FONT_LABEL);
        }
        return;
    }

    const WeatherData *weather = effectiveWeatherData();

    // Current conditions: temperature on the left, a hand-drawn weather glyph on the right.
    tft.fillRect(9, 64, 222, 91, theme.surface);
    tft.drawRect(9, 64, 222, 91, theme.accent);
    tft.drawRect(12, 67, 216, 85, theme.accentSoft);
    drawDisplayLabel(weather->location[0] != '\\0' ? weather->location : "DUISBURG // 47239",
                     18, 71, 204, TL_DATUM, theme.muted, FONT_INFO);
    const int temperatureFonts[] = {FONT_HUGE, FONT_TITLE, FONT_BODY, FONT_LABEL};
    drawAdaptiveText(formatWeatherTemperature(weather->temperature), 20, 88, 128,
                     TL_DATUM, temperatureFonts, 4, theme.text, theme.surface);

    String condition = weather->condition;
    condition.toLowerCase();
    const int cx = 181;
    const int cy = 105;
    if (condition.indexOf("rain") >= 0 || condition.indexOf("regen") >= 0 ||
        condition.indexOf("shower") >= 0 || condition.indexOf("drizzle") >= 0) {
        tft.drawCircle(cx - 8, cy - 5, 10, theme.accent);
        tft.drawCircle(cx + 5, cy - 8, 13, theme.accent);
        tft.drawCircle(cx + 17, cy - 3, 8, theme.accent);
        tft.drawFastHLine(cx - 16, cy + 2, 42, theme.accent);
        for (int i = 0; i < 3; ++i) {
            tft.drawLine(cx - 10 + i * 14, cy + 8, cx - 15 + i * 14, cy + 17, theme.text);
        }
    } else if (condition.indexOf("cloud") >= 0 || condition.indexOf("bewoelk") >= 0 ||
               condition.indexOf("overcast") >= 0 || condition.indexOf("nebel") >= 0) {
        tft.drawCircle(cx - 8, cy - 2, 10, theme.accent);
        tft.drawCircle(cx + 5, cy - 7, 13, theme.accent);
        tft.drawCircle(cx + 17, cy - 1, 8, theme.accent);
        tft.drawFastHLine(cx - 17, cy + 7, 43, theme.accent);
    } else {
        tft.drawCircle(cx, cy, 13, theme.accent);
        tft.drawCircle(cx, cy, 8, theme.text);
        for (int ray = 0; ray < 8; ++ray) {
            const float angle = ray * 0.785398f;
            const int x1 = cx + static_cast<int>(17 * cosf(angle));
            const int y1 = cy + static_cast<int>(17 * sinf(angle));
            const int x2 = cx + static_cast<int>(23 * cosf(angle));
            const int y2 = cy + static_cast<int>(23 * sinf(angle));
            tft.drawLine(x1, y1, x2, y2, theme.accent);
        }
    }

    drawDisplayLabel(weather->condition[0] != '\\0' ? weather->condition : "AKTUELLE LAGE",
                     120, 135, 204, TC_DATUM, theme.accent, FONT_INFO);
    String currentRange = "HOCH " + String(weather->high) + "C   TIEF " +
                          String(weather->low) + "C   REGEN " +
                          String(weather->rainChance) + "%";
    drawDisplayLabel(currentRange, 120, 146, 204, TC_DATUM, theme.text, FONT_INFO);

    drawDisplayLabel("VORHERSAGE // 3 TAGE", 10, 163, 220,
                     TL_DATUM, theme.accent, FONT_LABEL);
    tft.drawFastHLine(10, 177, 220, theme.accentSoft);

    for (uint8_t slot = 0; slot < 3; ++slot) {
        const int y = 181 + static_cast<int>(slot) * 15;
        if (slot > 0) tft.drawFastHLine(10, y - 2, 220, theme.surface);
        if (weather->forecastCount > slot + 1) {
            const WeatherForecastDay &day = weather->forecast[slot + 1];
            drawDisplayLabel(day.date, 12, y, 42, TL_DATUM, theme.text, FONT_INFO);
            drawDisplayLabel(day.condition, 58, y, 92, TL_DATUM, theme.muted, FONT_INFO);
            String range = String(day.low) + "/" + String(day.high) + "C";
            drawDisplayLabel(range, 174, y, 48, TR_DATUM, theme.text, FONT_INFO);
            drawDisplayLabel(String(day.rainChance) + "%", 230, y, 34,
                             TR_DATUM, theme.accent, FONT_INFO);
        } else {
            drawDisplayLabel("--.--", 12, y, 42, TL_DATUM, theme.muted, FONT_INFO);
            drawDisplayLabel("DATEN AUSSTEHEND", 58, y, 92, TL_DATUM, theme.muted, FONT_INFO);
            drawDisplayLabel("--/--", 174, y, 48, TR_DATUM, theme.muted, FONT_INFO);
            drawDisplayLabel("--", 230, y, 34, TR_DATUM, theme.muted, FONT_INFO);
        }
    }
}'''
s = replace_function(s, "void renderClockPage() {", "void renderMarketsPage() {", clock_weather)
display.write_text(s, encoding="utf-8")

# Remove the cartoon fallback entirely. If a real GIF cannot be decoded, the
# archive stays static rather than drawing a fake mascot/helmet.
s = gif.read_text(encoding="utf-8")
s = s.replace("bool fallbackAnimationActive = false;\nuint32_t fallbackFrameAtMs = 0;\n", "")
tick = r'''bool gifPlayerTick(uint32_t nowMs) {
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
        gifPlayerStop();
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
s = s.replace("    fallbackAnimationActive = false;\n    fallbackFrameAtMs = 0;\n", "")
s = s.replace("    return decoder != nullptr || fallbackAnimationActive;", "    return decoder != nullptr;")
start_next = r'''bool gifPlayerStartNext(TFT_eSPI &display) {
    if (gifFileListDirty) gifPlayerRefreshFiles();
    if (gifPathCount == 0) {
        Serial.println(F("GIF archive empty: no fallback animation"));
        return false;
    }

    const uint8_t attempts = gifPathCount;
    for (uint8_t attempt = 0; attempt < attempts; ++attempt) {
        const uint8_t selected = nextGifIndex;
        nextGifIndex = static_cast<uint8_t>((nextGifIndex + 1) % gifPathCount);
        if (gifPlayerStart(gifPaths[selected], display)) {
            Serial.printf("GIF started: %s\n", gifPaths[selected]);
            return true;
        }
    }
    Serial.println(F("GIF archive: no compatible GIF could be started"));
    return false;
}'''
s = replace_function(s, "bool gifPlayerStartNext(TFT_eSPI &display) {", "bool gifPlayerUploadStart(", start_next)
gif.write_text(s, encoding="utf-8")

# Play an actual stored GIF for a short interval after every page change.
# The normal GIF page continues to play the album for its full page duration.
s = main.read_text(encoding="utf-8")
needle = "uint32_t lastGifStartAttemptMs = 0;"
if needle not in s:
    raise SystemExit("Expected GIF integration state not found in main.cpp")
s = s.replace(needle, needle + """
uint8_t lastGifObservedPage = 0xFF;
bool gifPageStateInitialized = false;
bool gifTransitionActive = false;
uint32_t gifTransitionUntilMs = 0;
""", 1)

old_block = r'''    if (!wifiFailsafeMode &&
        !networkActionBusy &&
        !feedsBusy() &&
        !displayState.apMode &&
        displayState.currentPage == DASHBOARD_PAGE_GIF) {
        if (!gifPlayerIsActive() && millis() - lastGifStartAttemptMs >= 1000UL) {
            lastGifStartAttemptMs = millis();
            gifPlayerStartNext(tft);
        }
        if (gifPlayerIsActive()) gifPlayerTick(millis());
    } else if (gifPlayerIsActive()) {
        gifPlayerStop();
    }

    maybeEnableClockSprite();

    if (millis() - lastDisplayUpdate > DISPLAY_UPDATE_INTERVAL) {
        displayUpdate();
        lastDisplayUpdate = millis();
    }'''
new_block = r'''    const uint32_t nowMs = millis();
    if (!gifPageStateInitialized) {
        lastGifObservedPage = displayState.currentPage;
        gifPageStateInitialized = true;
    } else if (lastGifObservedPage != displayState.currentPage) {
        lastGifObservedPage = displayState.currentPage;
        gifTransitionActive = false;
        gifPlayerStop();
        if (!wifiFailsafeMode && !networkActionBusy && !feedsBusy() &&
            !displayState.apMode && displayState.currentPage != DASHBOARD_PAGE_GIF) {
            if (gifPlayerStartNext(tft)) {
                gifTransitionActive = true;
                gifTransitionUntilMs = nowMs + 1800UL;
            }
        }
    }

    if (!wifiFailsafeMode && !networkActionBusy && !feedsBusy() && !displayState.apMode) {
        if (displayState.currentPage == DASHBOARD_PAGE_GIF) {
            gifTransitionActive = false;
            if (!gifPlayerIsActive() && nowMs - lastGifStartAttemptMs >= 1000UL) {
                lastGifStartAttemptMs = nowMs;
                gifPlayerStartNext(tft);
            }
            if (gifPlayerIsActive()) gifPlayerTick(nowMs);
        } else if (gifTransitionActive) {
            if (static_cast<int32_t>(nowMs - gifTransitionUntilMs) >= 0) {
                gifPlayerStop();
                gifTransitionActive = false;
                lastDisplayUpdate = 0;
            } else {
                gifPlayerTick(nowMs);
            }
        } else if (gifPlayerIsActive()) {
            gifPlayerStop();
        }
    } else if (gifPlayerIsActive()) {
        gifPlayerStop();
        gifTransitionActive = false;
        lastDisplayUpdate = 0;
    }

    maybeEnableClockSprite();

    if (!gifTransitionActive && millis() - lastDisplayUpdate > DISPLAY_UPDATE_INTERVAL) {
        displayUpdate();
        lastDisplayUpdate = millis();
    }'''
if old_block not in s:
    raise SystemExit("Could not locate existing GIF page loop block")
s = s.replace(old_block, new_block, 1)
main.write_text(s, encoding="utf-8")

print("V7: larger weather text, collision-free footer, no fake animation, GIF page-transition playback")
