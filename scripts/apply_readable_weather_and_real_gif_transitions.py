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
        drawAdaptiveText(formatWeatherTemperature(weather->temperature), 64, 178, 78,
                         TL_DATUM, temperatureFonts, 2, theme.text, theme.surface);
        drawDisplayLabel(weather->condition[0] != '\0' ? weather->condition : "AKTUELL",
                         220, 180, 126, TR_DATUM, theme.text, FONT_LABEL);
        drawDisplayLabel(weather->location[0] != '\0' ? weather->location : "DUISBURG",
                         18, 198, 204, TL_DATUM, theme.muted, FONT_INFO);
    } else if (feedRuntime.weather.syncing || weatherWaitingForSync()) {
        drawDisplayLabel("WETTERDATEN WERDEN GELADEN",
                         120, 181, 204, TC_DATUM, theme.text, FONT_LABEL);
        drawDisplayLabel("OPEN-METEO // VERBINDUNG AKTIV",
                         120, 199, 204, TC_DATUM, theme.muted, FONT_INFO);
    } else if (feedRuntime.weather.lastError[0] != '\0') {
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
    drawScreenChrome("DATA // WASTELAND WEATHER");

    if (!hasWeatherContent()) {
        tft.drawRect(9, 70, 222, 125, theme.accent);
        tft.drawFastHLine(13, 92, 214, theme.accentSoft);
        drawDisplayLabel("WETTERDATENBANK", 120, 78, 208,
                         TC_DATUM, theme.accent, FONT_LABEL);
        if (feedRuntime.weather.syncing || weatherWaitingForSync()) {
            drawDisplayLabel("WETTERDATEN WERDEN GELADEN",
                             120, 119, 208, TC_DATUM, theme.text, FONT_LABEL);
            drawDisplayLabel("OPEN-METEO // LIVE-VERBINDUNG",
                             120, 146, 208, TC_DATUM, theme.muted, FONT_INFO);
        } else if (feedRuntime.weather.lastError[0] != '\0') {
            drawDisplayLabel("WETTERDATEN NICHT VERFUEGBAR",
                             120, 115, 208, TC_DATUM, theme.warning, FONT_LABEL);
            drawDisplayLabel(feedRuntime.weather.lastError,
                             120, 143, 208, TC_DATUM, theme.text, FONT_INFO);
        } else {
            drawDisplayLabel("KEINE WETTERDATEN EMPFANGEN",
                             120, 124, 208, TC_DATUM, theme.warning, FONT_LABEL);
        }
        return;
    }

    const WeatherData *weather = effectiveWeatherData();
    tft.drawRect(9, 69, 222, 80, theme.accent);
    tft.drawRect(12, 72, 216, 74, theme.accentSoft);
    drawDisplayLabel(weather->location[0] != '\0' ? weather->location : "DUISBURG",
                     120, 76, 208, TC_DATUM, theme.muted, FONT_LABEL);

    const int temperatureFonts[] = {FONT_BODY, FONT_LABEL};
    drawAdaptiveText(formatWeatherTemperature(weather->temperature), 120, 94, 170,
                     TC_DATUM, temperatureFonts, 2, theme.text, theme.background);
    drawDisplayLabel(weather->condition[0] != '\0' ? weather->condition : "AKTUELLE BEDINGUNGEN",
                     120, 129, 208, TC_DATUM, theme.accent, FONT_LABEL);

    drawDisplayLabel("VORHERSAGE // NAECHSTE 3 TAGE", 10, 155, 220,
                     TL_DATUM, theme.accent, FONT_LABEL);
    tft.drawFastHLine(10, 171, 220, theme.accentSoft);

    for (uint8_t slot = 0; slot < 3; ++slot) {
        const int y = 175 + static_cast<int>(slot) * 17;
        if (slot > 0) tft.drawFastHLine(10, y - 2, 220, theme.surface);
        if (weather->forecastCount > slot + 1) {
            const WeatherForecastDay &day = weather->forecast[slot + 1];
            drawDisplayLabel(day.date, 12, y, 54, TL_DATUM, theme.text, FONT_LABEL);
            String range = String(day.low) + " / " + String(day.high) + " C";
            drawDisplayLabel(range, 128, y, 112, TC_DATUM, theme.text, FONT_LABEL);
            drawDisplayLabel(String(day.rainChance) + "%",
                             228, y, 48, TR_DATUM, theme.accent, FONT_LABEL);
        } else {
            drawDisplayLabel("--.--", 12, y, 54, TL_DATUM, theme.muted, FONT_LABEL);
            drawDisplayLabel("-- / -- C", 128, y, 112, TC_DATUM, theme.muted, FONT_LABEL);
            drawDisplayLabel("--", 228, y, 48, TR_DATUM, theme.muted, FONT_LABEL);
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
