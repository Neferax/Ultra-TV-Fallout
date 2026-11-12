#!/usr/bin/env python3
"""Replace the three active SmallTV pages with a legible Pip-Boy 3000 layout."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
display = root / "src/display.cpp"

def replace_function(source, signature, next_signature, replacement):
    start = source.index(signature)
    end = source.index(next_signature, start)
    return source[:start] + replacement.rstrip() + "\n\n" + source[end:]

s = display.read_text(encoding="utf-8")

# Use explicit German weekday/month abbreviations; strftime locale is not
# guaranteed to be German on the ESP8266.
date_fn = r'''String formatLocalDate() {
    if (!hasTimeSync()) return "WARTET AUF ZEIT";
    static const char *weekdays[] = {"SO", "MO", "DI", "MI", "DO", "FR", "SA"};
    static const char *months[] = {"JAN", "FEB", "MAE", "APR", "MAI", "JUN",
                                   "JUL", "AUG", "SEP", "OKT", "NOV", "DEZ"};
    time_t now = time(nullptr);
    tm localInfo;
    localtime_r(&now, &localInfo);
    char buffer[32];
    snprintf(buffer, sizeof(buffer), "%s  %02d. %s %04d",
             weekdays[localInfo.tm_wday], localInfo.tm_mday,
             months[localInfo.tm_mon], localInfo.tm_year + 1900);
    return String(buffer);
}'''
s = replace_function(s, "String formatLocalDate() {", "String formatWorldTime(", date_fn)

clock_dynamic = r'''void updateClockDynamicArea() {
    const ThemePalette &theme = activeTheme();
    bool isPm = false;
    const String timeText = formatLocalTime(dashboardConfig.showSeconds,
                                            dashboardConfig.use24Hour, &isPm);
    tft.fillRect(17, 85, 206, 62, TFT_BLACK);
    drawClockTime(tft, timeText, dashboardConfig.showSeconds,
                  0xAFE5, 0x3DE7, TFT_BLACK, 120, 91);
    tft.drawFastHLine(24, 151, 192, 0x03E0);
}'''
s = replace_function(s, "void updateClockDynamicArea() {", "void drawDynamicText(", clock_dynamic)

chrome = r'''void drawScreenChrome(const String &title) {
    const ThemePalette &theme = activeTheme();
    tft.setTextSize(1);
    tft.fillScreen(TFT_BLACK);
    footerClockCache[0] = '\0';

    // Fallout 4 Pip-Boy: restrained phosphor, fixed register strip, no cards.
    tft.fillRect(0, 0, 240, 20, 0x0100);
    drawDisplayLabel("ROBCO", 8, 3, 90, TL_DATUM, 0x07E0, FONT_LABEL);
    drawDisplayLabel("PIP-OS", 232, 3, 90, TR_DATUM, 0xAFE5, FONT_LABEL);
    tft.drawFastHLine(8, 21, 224, 0x07E0);

    const char *tabs[] = {"STAT", "DATA", "RADIO"};
    const int centers[] = {42, 120, 198};
    const uint8_t active = displayState.currentPage == DASHBOARD_PAGE_WEATHER ? 1 :
                           displayState.currentPage == DASHBOARD_PAGE_GIF ? 2 : 0;
    for (uint8_t i = 0; i < 3; ++i) {
        const uint16_t color = i == active ? 0xAFE5 : 0x3DE7;
        drawDisplayLabel(tabs[i], centers[i], 27, 70, TC_DATUM, color, FONT_LABEL);
        if (i == active) tft.fillRect(centers[i] - 23, 44, 46, 3, 0x07E0);
    }
    tft.drawFastHLine(8, 49, 224, 0x03E0);
    drawDisplayLabel(title, 10, 56, 220, TL_DATUM, 0x07E0, FONT_LABEL);
    tft.drawFastHLine(8, 218, 224, 0x03E0);
    drawDisplayLabel("VAULT-TEC", 8, 220, 120, TL_DATUM, 0x3DE7, FONT_LABEL);
    drawDisplayLabel("MK IV", 232, 220, 60, TR_DATUM, 0x3DE7, FONT_LABEL);
    // No moving footer clock: reserve the bottom strip for stable device identity.
}'''
s = replace_function(s, "void drawScreenChrome(const String &title) {", "void drawPlaceholder(", chrome)

clock = r'''void renderClockPage() {
    const ThemePalette &theme = activeTheme();
    drawScreenChrome("STAT // STATUS");
    clockMetaCache.valid = false;
    bool isPm = false;
    const String timeText = formatLocalTime(dashboardConfig.showSeconds,
                                            dashboardConfig.use24Hour, &isPm);

    // The clock is the hero element. No weather card competes with it.
    tft.drawRect(12, 78, 216, 82, 0x03E0);
    tft.drawRect(15, 81, 210, 76, 0x0100);
    drawClockTime(tft, timeText, dashboardConfig.showSeconds,
                  0xAFE5, 0x3DE7, TFT_BLACK, 120, 93);
    tft.drawFastHLine(24, 166, 192, 0x03E0);
    drawDisplayLabel(formatLocalDate(), 120, 178, 216, TC_DATUM,
                     0xAFE5, FONT_LABEL);
    // Keep the lower display area clear; date is the only secondary clock line.
}'''
s = replace_function(s, "void renderClockPage() {", "void renderWeatherPage() {", clock)

weather = r'''void renderWeatherPage() {
    const ThemePalette &theme = activeTheme();
    drawScreenChrome("DATA // WEATHER");
    if (!hasWeatherContent()) {
        tft.drawRect(12, 78, 216, 110, 0x03E0);
        drawDisplayLabel("WEATHER LINK", 120, 96, 200, TC_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel(feedRuntime.weather.syncing ? "CONNECTING..." :
                         feedRuntime.weather.lastError[0] ? "DATA UNAVAILABLE" :
                         "WAITING FOR DATA",
                         120, 132, 200, TC_DATUM, 0x3DE7, FONT_LABEL);
        drawDisplayLabel("OPEN-METEO // 47239", 120, 164, 200,
                         TC_DATUM, 0x3DE7, FONT_INFO);
        return;
    }

    const WeatherData *weather = effectiveWeatherData();
    // Current temperature and condition use the largest free area.
    drawDisplayLabel(weather->location[0] ? weather->location : "DUISBURG // 47239",
                     12, 78, 216, TL_DATUM, 0x3DE7, FONT_LABEL);
    const int heroFonts[] = {FONT_HUGE, FONT_TITLE, FONT_BODY};
    drawAdaptiveText(formatWeatherTemperature(weather->temperature), 12, 96, 122,
                     TL_DATUM, heroFonts, 3, 0xAFE5, TFT_BLACK);

    String condition = weather->condition;
    condition.toUpperCase();
    if (condition.length() > 15) while (condition.length() > 15) condition.remove(condition.length() - 1);
    drawDisplayLabel(condition, 232, 116, 92, TR_DATUM, 0x07E0, FONT_INFO);

    tft.drawFastHLine(12, 151, 216, 0x03E0);
    drawDisplayLabel("HOCH", 48, 159, 64, TC_DATUM, 0x3DE7, FONT_INFO);
    drawDisplayLabel("TIEF", 120, 159, 64, TC_DATUM, 0x3DE7, FONT_INFO);
    drawDisplayLabel("REGEN", 192, 159, 64, TC_DATUM, 0x3DE7, FONT_INFO);
    drawDisplayLabel(String(weather->high) + "C", 48, 174, 64, TC_DATUM, 0xAFE5, FONT_LABEL);
    drawDisplayLabel(String(weather->low) + "C", 120, 174, 64, TC_DATUM, 0xAFE5, FONT_LABEL);
    drawDisplayLabel(String(weather->rainChance) + "%", 192, 174, 64, TC_DATUM, 0xAFE5, FONT_LABEL);

    drawDisplayLabel("VORHERSAGE", 12, 193, 216, TL_DATUM, 0x07E0, FONT_INFO);
    if (weather->forecastCount > 1) {
        const WeatherForecastDay &day = weather->forecast[1];
        String row = String(day.date) + "   " + String(day.low) + "/" +
                     String(day.high) + "C   " + String(day.rainChance) + "%";
        drawDisplayLabel(row, 12, 207, 216, TL_DATUM, 0xAFE5, FONT_INFO);
    } else {
        drawDisplayLabel("--.--    --/--C    --%", 12, 207, 216,
                         TL_DATUM, 0x3DE7, FONT_INFO);
    }
}'''
s = replace_function(s, "void renderWeatherPage() {", "void renderMarketsPage() {", weather)

display.write_text(s, encoding="utf-8")
print("Pip-Boy V2: clean STAT, DATA and RADIO register layout applied")
