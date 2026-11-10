#!/usr/bin/env python3
"""Replace the stock clock/weather renderers with the Fallout Pip-Boy layout."""
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")
replacement = r'''void renderClockPage() {
    const ThemePalette &theme = activeTheme();
    drawScreenChrome("ROBCO // PIP-OS 3000");
    clockMetaCache.valid = false;
    updateClockDynamicArea();
    tft.drawRect(2, 34, 236, 174, theme.accent);
    tft.drawRect(5, 37, 230, 168, theme.accentSoft);
    tft.fillRect(7, 39, 226, 18, theme.surface);
    drawDisplayLabel("ROBCO INDUSTRIES", 12, 42, 145, TL_DATUM, theme.accent, FONT_INFO);
    drawDisplayLabel("PIP-OS 3000", 228, 42, 90, TR_DATUM, theme.text, FONT_INFO);
    tft.drawFastHLine(8, 60, 224, theme.accent);
    drawDisplayLabel("STATUS // LOCAL TIME", 12, 64, 216, TL_DATUM, theme.muted, FONT_INFO);
    tft.drawRect(10, 78, 220, 58, theme.accent);
    tft.drawFastHLine(14, 139, 212, theme.accentSoft);
    drawDisplayLabel("ENVIRONMENTAL READOUT", 12, 145, 216, TL_DATUM, theme.accent, FONT_INFO);
    const char *message = activeClockMessage();
    if (hasWeatherContent()) {
        const WeatherData *weather = effectiveWeatherData();
        tft.fillRect(12, 160, 216, 38, theme.surface);
        tft.drawRect(12, 160, 216, 38, theme.accent);
        drawDisplayLabel(formatWeatherTemperature(weather->temperature), 18, 165, 96,
                         TL_DATUM, theme.text, FONT_BODY);
        drawDisplayLabel(weather->condition[0] != '\\0' ? weather->condition : "WEATHER",
                         222, 169, 104, TR_DATUM, theme.accent, FONT_INFO);
        drawDisplayLabel("DUISBURG // RUMLN", 120, 185, 204, TC_DATUM, theme.muted, FONT_INFO);
    } else if (weatherWaitingForSync()) {
        tft.drawRect(12, 160, 216, 38, theme.accent);
        drawDisplayLabel("ACQUIRING DATA...", 120, 174, 204, TC_DATUM, theme.muted, FONT_INFO);
    } else if (message != nullptr) {
        drawDisplayLabel("ENVIRONMENTAL DATA OFFLINE", 120, 174, 204,
                         TC_DATUM, theme.warning, FONT_INFO);
    } else {
        drawDisplayLabel("NO DATA", 120, 174, 204, TC_DATUM, theme.muted, FONT_INFO);
    }
    drawDisplayLabel("VAULT-TEC PERSONNEL RECORD", 12, 211, 216, TL_DATUM, theme.muted, FONT_INFO);
}

void renderWeatherPage() {
    const ThemePalette &theme = activeTheme();
    if (!hasWeatherContent()) {
        drawScreenChrome("ROBCO // WEATHER");
        tft.drawRect(2, 34, 236, 174, theme.accent);
        tft.drawRect(5, 37, 230, 168, theme.accentSoft);
        tft.fillRect(7, 39, 226, 18, theme.surface);
        drawDisplayLabel("ROBCO // WEATHER", 12, 42, 216, TL_DATUM, theme.accent, FONT_INFO);
        tft.drawFastHLine(8, 60, 224, theme.accent);
        drawDisplayLabel("METEOROLOGICAL DATABASE", 12, 72, 216, TL_DATUM, theme.text, FONT_INFO);
        drawDisplayLabel(weatherWaitingForSync() ? "CONNECTING TO METEOROLOGICAL FEED"
                                                 : "NO WEATHER DATA CONFIGURED",
                         120, 118, 216, TC_DATUM, theme.text, FONT_LABEL);
        tft.drawRect(12, 151, 216, 36, theme.accent);
        drawDisplayLabel("OPEN-METEO // LIVE FEED", 120, 164, 204, TC_DATUM, theme.muted, FONT_INFO);
        return;
    }
    const WeatherData *weather = effectiveWeatherData();
    drawScreenChrome("ROBCO // WEATHER");
    tft.drawRect(2, 34, 236, 174, theme.accent);
    tft.drawRect(5, 37, 230, 168, theme.accentSoft);
    tft.fillRect(7, 39, 226, 18, theme.surface);
    drawDisplayLabel("ROBCO // WEATHER", 12, 42, 216, TL_DATUM, theme.accent, FONT_INFO);
    drawDisplayLabel(weather->location[0] != '\\0' ? weather->location : "UNKNOWN",
                     120, 64, 216, TC_DATUM, theme.muted, FONT_INFO);
    tft.drawFastHLine(10, 82, 220, theme.accent);
    drawDisplayLabel("CURRENT CONDITIONS", 12, 89, 216, TL_DATUM, theme.accent, FONT_INFO);
    tft.drawRect(12, 104, 216, 48, theme.accent);
    drawHeroText(formatWeatherTemperature(weather->temperature), 108, 40, theme.text, 3);
    drawDisplayLabel(weather->condition[0] != '\\0' ? weather->condition : "UPDATED",
                     120, 158, 216, TC_DATUM, theme.accent, FONT_LABEL);
    tft.drawFastHLine(10, 176, 220, theme.accent);
    const int valueFonts[] = {FONT_BODY, FONT_LABEL};
    const String values[] = {formatWeatherTemperature(weather->high),
                             formatWeatherTemperature(weather->low), String(weather->rainChance) + "%"};
    const char *labels[] = {"HIGH", "LOW", "RAIN"};
    for (uint8_t index = 0; index < 3; ++index) {
        int centerX = 40 + index * 80;
        tft.drawRect(centerX - 34, 180, 68, 23, theme.accent);
        drawDisplayLabel(labels[index], centerX, 181, 64, TC_DATUM, theme.muted, FONT_INFO);
        drawAdaptiveText(values[index], centerX, 191, 64, TC_DATUM,
                         valueFonts, sizeof(valueFonts) / sizeof(valueFonts[0]), theme.text, theme.background);
    }
}'''

start = source.index("void renderClockPage() {")
end = source.index("void renderMarketsPage() {", start)
updated = source[:start] + replacement + "\n\n" + source[end:]
path.write_text(updated, encoding="utf-8")
print("Pip-Boy clock and weather renderers applied")
