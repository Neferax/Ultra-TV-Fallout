#!/usr/bin/env python3
"""Apply the complete Fallout Pip-Boy UI to the SmallTV renderer."""
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")

def replace_function(source: str, signature: str, next_signature: str, replacement: str) -> str:
    start = source.index(signature)
    end = source.index(next_signature, start)
    return source[:start] + replacement.rstrip() + "\n\n" + source[end:]

# Monochrome green phosphor palette with visibly different panel levels.
source = replace_function(
    source,
    "const ThemePalette& activeTheme() {",
    "String safeCString(",
    r'''const ThemePalette& activeTheme() {
    static const ThemePalette pipBoyTheme = {
        0x0000, // black glass
        0x0100, // dark phosphor panel
        0x0200, // raised panel
        0x07E0, // phosphor green
        0x03E0, // dim green
        0xAFE5, // pale phosphor text
        0x5FEC, // subdued green
        0x07E0,
        0x5FEC,
        0x07E0
    };
    return pipBoyTheme;
}'''
)

# The native clock updater is repositioned as well; otherwise the stock y=44
# sprite region overwrites the new HUD layout.
source = replace_function(
    source,
    "void updateClockDynamicArea() {",
    "void drawDynamicText(",
    r'''void updateClockDynamicArea() {
    const ThemePalette &theme = activeTheme();
    bool isPm = false;
    String timeText = formatLocalTime(dashboardConfig.showSeconds, dashboardConfig.use24Hour, &isPm);
    String metaLine = formatClockMetaLine(isPm);

    tft.fillRect(13, 59, 214, 82, theme.background);
    drawDisplayLabel(metaLine, 120, 61, 208, TC_DATUM, theme.muted, FONT_LABEL);
    drawClockTime(tft, timeText, dashboardConfig.showSeconds,
                  theme.text, theme.muted, theme.background, 120, 82);
    tft.drawFastHLine(20, 140, 200, theme.accentSoft);
    clockMetaCache.valid = true;
    strncpy(clockMetaCache.metaLine, metaLine.c_str(), sizeof(clockMetaCache.metaLine) - 1);
    clockMetaCache.metaLine[sizeof(clockMetaCache.metaLine) - 1] = '\0';
}'''
)

# Keep the original clock cache mechanism, but use a Pip-Boy segmented HUD.
source = replace_function(
    source,
    "void drawScreenChrome(const String &title) {",
    "void drawPlaceholder(",
    r'''void drawScreenChrome(const String &title) {
    const ThemePalette &theme = activeTheme();
    tft.setTextSize(1);
    tft.fillScreen(theme.background);
    footerClockCache[0] = '\0';

    // RobCo identification strip.
    tft.fillRect(0, 0, 240, 22, theme.surface);
    tft.drawFastHLine(0, 22, 240, theme.accent);
    drawDisplayLabel("ROBCO INDUSTRIES", 8, 6, 132, TL_DATUM, theme.accent, FONT_INFO);
    drawDisplayLabel("PIP-OS 3000", 232, 6, 94, TR_DATUM, theme.text, FONT_INFO);

    // Pip-Boy's STAT / DATA / RADIO navigation strip.
    const char *tabA = "STAT";
    const char *tabB = "DATA";
    const char *tabC = "RADIO";
    uint8_t activeTab = displayState.currentPage == DASHBOARD_PAGE_WEATHER ? 1 :
                        displayState.currentPage == DASHBOARD_PAGE_GIF ? 2 : 0;
    const int tabX[] = {8, 86, 164};
    const char *tabText[] = {tabA, tabB, tabC};
    for (uint8_t i = 0; i < 3; ++i) {
        uint16_t color = i == activeTab ? theme.text : theme.muted;
        drawDisplayLabel(tabText[i], tabX[i] + 32, 29, 64, TC_DATUM, color, FONT_LABEL);
        if (i == activeTab) {
            tft.fillRect(tabX[i] + 5, 43, 54, 2, theme.accent);
        } else {
            tft.drawFastHLine(tabX[i] + 10, 43, 44, theme.accentSoft);
        }
    }
    tft.drawFastHLine(8, 47, 224, theme.accentSoft);
    drawDisplayLabel(title, 10, 51, 220, TL_DATUM, theme.accent, FONT_INFO);

    // Small corner ticks and the characteristic terminal footer.
    tft.drawFastVLine(5, 54, 150, theme.accentSoft);
    tft.drawFastVLine(234, 54, 150, theme.accentSoft);
    tft.drawFastHLine(8, 207, 224, theme.accent);
    tft.drawFastHLine(8, 209, 224, theme.accentSoft);
    drawDisplayLabel("VAULT-TEC // PERSONNEL DEVICE", 232, 219, 128,
                     TR_DATUM, theme.muted, FONT_INFO);
    if (displayState.currentPage != DASHBOARD_PAGE_CLOCK || temporaryMessageVisible()) {
        updateFooterClock();
    }
}'''
)

clock_weather = r'''void renderClockPage() {
    const ThemePalette &theme = activeTheme();
    drawScreenChrome("STATUS // LOCAL TIME");
    clockMetaCache.valid = false;

    // Main Pip-Boy time instrument.
    tft.drawRect(8, 68, 224, 80, theme.accent);
    tft.drawRect(11, 71, 218, 74, theme.accentSoft);
    updateClockDynamicArea();

    // Live environmental status card.
    tft.fillRect(10, 155, 220, 44, theme.surface);
    tft.drawRect(10, 155, 220, 44, theme.accentSoft);
    drawDisplayLabel("ENVIRONMENTAL DATA", 18, 158, 204,
                     TL_DATUM, theme.accent, FONT_INFO);
    const char *message = activeClockMessage();
    if (hasWeatherContent()) {
        const WeatherData *weather = effectiveWeatherData();
        drawDisplayLabel(formatWeatherTemperature(weather->temperature), 18, 174, 78,
                         TL_DATUM, theme.text, FONT_BODY);
        drawDisplayLabel(weather->condition[0] != '\0' ? weather->condition : "WEATHER",
                         220, 176, 112, TR_DATUM, theme.accent, FONT_LABEL);
        drawDisplayLabel("DUISBURG // RUMELN-KALDENHAUSEN", 120, 188, 204,
                         TC_DATUM, theme.muted, FONT_INFO);
    } else if (feedRuntime.weather.syncing || weatherWaitingForSync()) {
        drawDisplayLabel("WEATHER LINK // SYNCING", 120, 176, 204,
                         TC_DATUM, theme.text, FONT_LABEL);
        drawDisplayLabel("OPEN-METEO", 120, 190, 204,
                         TC_DATUM, theme.muted, FONT_INFO);
    } else if (feedRuntime.weather.lastError[0] != '\0') {
        drawDisplayLabel("WEATHER LINK // ERROR", 120, 174, 204,
                         TC_DATUM, theme.warning, FONT_LABEL);
        drawDisplayLabel(feedRuntime.weather.lastError, 120, 188, 204,
                         TC_DATUM, theme.text, FONT_INFO);
    } else if (message != nullptr) {
        drawDisplayLabel("EXTERNAL DATA OFFLINE", 120, 179, 204,
                         TC_DATUM, theme.warning, FONT_LABEL);
    } else {
        drawDisplayLabel("WEATHER FEED // WAITING", 120, 179, 204,
                         TC_DATUM, theme.muted, FONT_LABEL);
    }
    drawDisplayLabel("PIP-BOY 3000 // MK IV", 12, 218, 130,
                     TL_DATUM, theme.accent, FONT_INFO);
}

void renderWeatherPage() {
    const ThemePalette &theme = activeTheme();
    drawScreenChrome("DATA // WASTELAND WEATHER");

    if (!hasWeatherContent()) {
        tft.drawRect(10, 70, 220, 116, theme.accent);
        tft.drawFastHLine(14, 91, 212, theme.accentSoft);
        drawDisplayLabel("METEOROLOGICAL DATABASE", 120, 77, 204,
                         TC_DATUM, theme.accent, FONT_INFO);
        if (feedRuntime.weather.lastError[0] != '\0') {
            drawDisplayLabel("WEATHER LINK // ERROR", 120, 113, 204,
                             TC_DATUM, theme.warning, FONT_LABEL);
            drawDisplayLabel(feedRuntime.weather.lastError, 120, 132, 204,
                             TC_DATUM, theme.text, FONT_INFO);
        } else {
            drawDisplayLabel(feedRuntime.weather.syncing ? "ESTABLISHING DATA LINK"
                                                         : "NO WEATHER DATA RECEIVED",
                             120, 119, 204, TC_DATUM, theme.text, FONT_LABEL);
        }
        drawDisplayLabel("OPEN-METEO // LIVE FEED", 120, 164, 204,
                         TC_DATUM, theme.muted, FONT_INFO);
        return;
    }

    const WeatherData *weather = effectiveWeatherData();
    tft.drawRect(9, 69, 222, 77, theme.accent);
    tft.drawRect(12, 72, 216, 71, theme.accentSoft);
    drawDisplayLabel(weather->location[0] != '\0' ? weather->location : "UNKNOWN LOCATION",
                     120, 76, 204, TC_DATUM, theme.muted, FONT_INFO);

    // Current conditions: a compact instrument panel.
    tft.drawCircle(47, 108, 14, theme.accent);
    tft.drawCircle(47, 108, 9, theme.accentSoft);
    tft.drawFastHLine(47, 88, 1, theme.accent);
    tft.drawFastHLine(47, 128, 1, theme.accent);
    tft.drawFastVLine(27, 108, 1, theme.accent);
    tft.drawFastVLine(67, 108, 1, theme.accent);
    const int temperatureFonts[] = {FONT_BODY, FONT_LABEL};
    drawAdaptiveText(formatWeatherTemperature(weather->temperature), 157, 98, 132,
                     TC_DATUM, temperatureFonts, 2, theme.text, theme.background);
    drawDisplayLabel(weather->condition[0] != '\0' ? weather->condition : "CURRENT CONDITIONS",
                     120, 129, 204, TC_DATUM, theme.accent, FONT_INFO);

    drawDisplayLabel("NEXT 3 DAYS // FORECAST", 10, 151, 220,
                     TL_DATUM, theme.accent, FONT_INFO);
    for (uint8_t slot = 0; slot < 3; ++slot) {
        const int left = 10 + slot * 74;
        tft.drawRect(left, 164, 68, 39, theme.accent);
        tft.fillRect(left + 2, 166, 64, 9, theme.surface);
        if (weather->forecastCount > slot + 1) {
            const WeatherForecastDay &day = weather->forecast[slot + 1];
            drawDisplayLabel(day.date, left + 34, 167, 62, TC_DATUM,
                             theme.accent, FONT_INFO);
            String range = String(day.high) + " / " + String(day.low) + " C";
            drawDisplayLabel(range, left + 34, 179, 62, TC_DATUM,
                             theme.text, FONT_INFO);
            drawDisplayLabel(String("RAIN ") + String(day.rainChance) + "%",
                             left + 34, 191, 62, TC_DATUM,
                             theme.muted, FONT_INFO);
        } else {
            drawDisplayLabel("--", left + 34, 180, 62, TC_DATUM,
                             theme.muted, FONT_INFO);
        }
    }
    drawDisplayLabel("OPEN-METEO // 4-DAY DATA", 230, 218, 128,
                     TR_DATUM, theme.muted, FONT_INFO);
}'''
# Remove accidental placeholder line before writing generated script.
clock_weather = clock_weather.replace("    tft.drawHeroText; // placeholder removed below\n", "")
source = replace_function(source, "void renderClockPage() {", "void renderMarketsPage() {", clock_weather)

path.write_text(source, encoding="utf-8")
print("Fallout Pip-Boy renderer and clock data layout applied")
