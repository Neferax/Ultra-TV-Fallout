#!/usr/bin/env python3
"""Apply the complete monochrome Pip-Boy visual system to the SmallTV renderer."""
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")

def replace_function(source: str, signature: str, next_signature: str, replacement: str) -> str:
    start = source.index(signature)
    end = source.index(next_signature, start)
    return source[:start] + replacement.rstrip() + "\n\n" + source[end:]

# Fixed phosphor palette: do not let a saved Aurora/custom theme dilute the Pip-Boy look.
source = replace_function(
    source,
    "const ThemePalette& activeTheme() {",
    "String safeCString(",
    r'''const ThemePalette& activeTheme() {
    static const ThemePalette pipBoyTheme = {
        0x0000, // deep black background
        0x0100, // near-black green panel
        0x0200, // secondary panel
        0x07E0, // phosphor green
        0x03E0, // dim phosphor
        0xB7F6, // readable pale green
        0x5FEC, // subdued green
        0x07E0, // positive
        0x5FEC, // negative rendered in monochrome
        0x07E0  // warning
    };
    return pipBoyTheme;
}'''
)

# Shared RobCo shell for every native dashboard page, not just clock/weather.
source = replace_function(
    source,
    "void drawScreenChrome(const String &title) {",
    "void drawPlaceholder(",
    r'''void drawScreenChrome(const String &title) {
    const ThemePalette &theme = activeTheme();
    tft.setTextSize(1);
    tft.fillScreen(theme.background);
    footerClockCache[0] = '\0';

    // Hardware-terminal bezel and fixed RobCo identity strip.
    tft.drawRect(1, 1, 238, 238, theme.accentSoft);
    tft.drawRect(3, 3, 234, 234, theme.accent);
    tft.fillRect(5, 5, 230, 17, theme.surface);
    drawDisplayLabel("ROBCO INDUSTRIES", 10, 7, 126, TL_DATUM, theme.accent, FONT_INFO);
    drawDisplayLabel("PIP-OS 3000", 230, 7, 104, TR_DATUM, theme.text, FONT_INFO);
    tft.drawFastHLine(7, 23, 226, theme.accent);
    drawDisplayLabel(title, 10, 26, 220, TL_DATUM, theme.text, FONT_INFO);

    // Side rails, corner ticks and Vault-Tec footer establish one visual language.
    tft.drawFastVLine(5, 43, 162, theme.accentSoft);
    tft.drawFastVLine(234, 43, 162, theme.accentSoft);
    tft.drawFastHLine(7, 207, 226, theme.accent);
    tft.drawFastHLine(7, 209, 226, theme.accentSoft);
    drawDisplayLabel("VAULT-TEC // PERSONNEL TERMINAL", 230, 218, 220,
                     TR_DATUM, theme.muted, FONT_INFO);
    footerClockCache[0] = '\0';
    if (displayState.currentPage != DASHBOARD_PAGE_CLOCK || temporaryMessageVisible()) {
        updateFooterClock();
    }
}'''
)

# Rebuild the two primary pages around the shared RobCo shell. All other existing
# pages inherit the same shell and phosphor palette through drawScreenChrome().
clock_weather = r'''void renderClockPage() {
    const ThemePalette &theme = activeTheme();
    drawScreenChrome("SYSTEM CLOCK // LOCAL TIME");
    clockMetaCache.valid = false;
    updateClockDynamicArea();

    // Instrument panel below the native clock readout.
    tft.drawRect(10, 145, 220, 54, theme.accent);
    tft.drawFastHLine(12, 158, 216, theme.accentSoft);
    drawDisplayLabel("ENVIRONMENTAL READOUT", 16, 148, 208,
                     TL_DATUM, theme.accent, FONT_INFO);

    const char *message = activeClockMessage();
    if (hasWeatherContent()) {
        const WeatherData *weather = effectiveWeatherData();
        tft.fillRect(14, 163, 212, 31, theme.surface);
        drawDisplayLabel(formatWeatherTemperature(weather->temperature), 20, 167, 82,
                         TL_DATUM, theme.text, FONT_BODY);
        drawDisplayLabel(weather->condition[0] != '\0' ? weather->condition : "WEATHER",
                         220, 170, 108, TR_DATUM, theme.accent, FONT_INFO);
        drawDisplayLabel("DUISBURG // RUMLN-KALDENHAUSEN", 120, 184, 204,
                         TC_DATUM, theme.muted, FONT_INFO);
    } else if (weatherWaitingForSync()) {
        drawDisplayLabel("ACQUIRING EXTERNAL DATA...", 120, 176, 204,
                         TC_DATUM, theme.muted, FONT_INFO);
    } else if (message != nullptr) {
        drawWrappedCenteredText(message, 120, 165, 204, FONT_LABEL,
                                theme.text, theme.background, 3, 30);
    } else {
        drawDisplayLabel("NO EXTERNAL DATA", 120, 176, 204,
                         TC_DATUM, theme.muted, FONT_INFO);
    }
}

void renderWeatherPage() {
    const ThemePalette &theme = activeTheme();
    if (!hasWeatherContent()) {
        drawScreenChrome("WEATHER // EXTERNAL FEED");
        tft.drawRect(12, 58, 216, 112, theme.accent);
        drawDisplayLabel("METEOROLOGICAL DATABASE", 120, 76, 204,
                         TC_DATUM, theme.accent, FONT_INFO);
        drawDisplayLabel(weatherWaitingForSync() ? "CONNECTING TO LIVE FEED"
                                                 : "NO WEATHER DATA CONFIGURED",
                         120, 116, 204, TC_DATUM, theme.text, FONT_LABEL);
        drawDisplayLabel("OPEN-METEO // DATA LINK", 120, 150, 204,
                         TC_DATUM, theme.muted, FONT_INFO);
        return;
    }

    const WeatherData *weather = effectiveWeatherData();
    drawScreenChrome("WEATHER // EXTERNAL FEED");
    drawDisplayLabel(weather->location[0] != '\0' ? weather->location : "UNKNOWN LOCATION",
                     120, 48, 212, TC_DATUM, theme.muted, FONT_INFO);
    tft.drawRect(12, 65, 216, 76, theme.accent);
    drawDisplayLabel("CURRENT CONDITIONS", 20, 70, 200,
                     TL_DATUM, theme.accent, FONT_INFO);
    drawHeroText(formatWeatherTemperature(weather->temperature), 111, 34, theme.text, 3);
    drawDisplayLabel(weather->condition[0] != '\0' ? weather->condition : "UPDATED",
                     120, 145, 212, TC_DATUM, theme.accent, FONT_LABEL);

    const int valueFonts[] = {FONT_BODY, FONT_LABEL};
    const String values[] = {formatWeatherTemperature(weather->high),
                             formatWeatherTemperature(weather->low),
                             String(weather->rainChance) + "%"};
    const char *labels[] = {"MAX", "MIN", "RAIN"};
    for (uint8_t index = 0; index < 3; ++index) {
        int left = 12 + index * 74;
        tft.drawRect(left, 166, 68, 34, theme.accent);
        drawDisplayLabel(labels[index], left + 34, 169, 62,
                         TC_DATUM, theme.muted, FONT_INFO);
        drawAdaptiveText(values[index], left + 34, 182, 62, TC_DATUM,
                         valueFonts, sizeof(valueFonts) / sizeof(valueFonts[0]),
                         theme.text, theme.background);
    }
}'''
source = replace_function(source, "void renderClockPage() {", "void renderMarketsPage() {", clock_weather)

path.write_text(source, encoding="utf-8")
print("Full Pip-Boy palette and shared RobCo shell applied to all dashboard pages")
