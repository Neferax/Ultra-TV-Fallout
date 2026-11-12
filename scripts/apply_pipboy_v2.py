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
    const bool forecastPage = ((millis() / 12000UL) % 2UL) != 0;
    drawScreenChrome(forecastPage ? "DATA // 3-TAGE-VORSCHAU" : "DATA // HEUTE");
    if (!hasWeatherContent()) {
        tft.drawRect(12, 78, 216, 110, 0x03E0);
        drawDisplayLabel("WETTER LINK", 120, 96, 200, TC_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel(feedRuntime.weather.syncing ? "VERBINDUNG..." :
                         feedRuntime.weather.lastError[0] ? "DATEN NICHT VERFUEGBAR" :
                         "WARTE AUF DATEN",
                         120, 132, 200, TC_DATUM, 0x3DE7, FONT_LABEL);
        drawDisplayLabel("OPEN-METEO // 47239", 120, 164, 200,
                         TC_DATUM, 0x3DE7, FONT_LABEL);
        return;
    }

    const WeatherData *weather = effectiveWeatherData();
    if (!forecastPage) {
        drawDisplayLabel(weather->location[0] ? weather->location : "DUISBURG // 47239",
                         12, 76, 216, TL_DATUM, 0x3DE7, FONT_LABEL);

        String temperature = String(weather->temperature);
        const int heroFonts[] = {FONT_BODY, FONT_LABEL};
        drawAdaptiveText(temperature, 12, 92, 130,
                         TL_DATUM, heroFonts, 2, 0xAFE5, TFT_BLACK);
        String unit;
        unit += weatherUnitSymbol();
        drawDisplayLabel(unit, 12 + tft.textWidth(temperature, FONT_BODY) + 5,
                         98, 36, TL_DATUM, 0xAFE5, FONT_BODY);

        String condition = weather->condition;
        if (condition == "Partly cloudy") condition = "TEILWEISE BEWOELKT";
        else if (condition == "Mostly cloudy") condition = "STARK BEWOELKT";
        else if (condition == "Cloudy" || condition == "Overcast") condition = "BEWOELKT";
        else if (condition == "Clear" || condition == "Mainly clear") condition = "KLAR";
        else if (condition == "Rain") condition = "REGEN";
        else if (condition == "Drizzle") condition = "NIESELREGEN";
        else if (condition == "Snow") condition = "SCHNEE";
        else if (condition == "Fog") condition = "NEBEL";
        condition.toUpperCase();
        if (condition.length() > 19) condition = "WETTERLAGE";
        drawDisplayLabel(condition, 12, 126, 216, TL_DATUM, 0x07E0, FONT_LABEL);

        const int direction = ((weather->windDirection + 22) / 45) % 8;
        const char *directions[] = {"N", "NO", "O", "SO", "S", "SW", "W", "NW"};
        String wind = "WIND " + String(directions[direction]) + " " + String(weather->windSpeed) + " KM/H";
        String gust = "BOEEN " + String(weather->windGusts);
        String feel = "GEFUEHLT " + String(weather->feelsLike) + weatherUnitSymbol();
        String humidity = "FEUCHTE " + String(weather->humidity) + "%";
        String precipitation = "REGEN " + String(weather->precipitation / 10) + "." +
                               String(abs(weather->precipitation % 10)) + " MM";
        String chance = "CHANCE " + String(weather->rainChance) + "%";
        String uv = "UV " + String(weather->uvIndex);
        drawDisplayLabel(feel, 12, 143, 108, TL_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel(humidity, 228, 143, 108, TR_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel(wind, 12, 160, 130, TL_DATUM, 0x3DE7, FONT_LABEL);
        drawDisplayLabel(gust, 228, 160, 100, TR_DATUM, 0x3DE7, FONT_LABEL);
        drawDisplayLabel(precipitation, 12, 177, 108, TL_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel(chance, 228, 177, 108, TR_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel(uv, 12, 194, 70, TL_DATUM, 0x3DE7, FONT_LABEL);
        String sun = "SONNE " + String(weather->sunrise) + "-" + String(weather->sunset);
        drawDisplayLabel(sun, 228, 194, 140, TR_DATUM, 0x3DE7, FONT_LABEL);
        return;
    }

    const char *labels[] = {"MORGEN", "UEBERMORGEN", "IN 3 TAGEN"};
    // Compact rows keep all three rain lines above the fixed footer.
    for (uint8_t slot = 0; slot < 3; ++slot) {
        const int y = 64 + static_cast<int>(slot) * 45;
        if (slot > 0) tft.drawFastHLine(12, y - 6, 216, 0x03E0);
        if (weather->forecastCount > slot + 1) {
            const WeatherForecastDay &day = weather->forecast[slot + 1];
            String heading = String(labels[slot]) + " // " + String(day.date);
            drawDisplayLabel(heading, 12, y, 216, TL_DATUM, 0x07E0, FONT_LABEL);
            String condition = day.condition;
            if (condition == "Partly cloudy") condition = "TEILWOLKIG";
            else if (condition == "Mostly cloudy") condition = "STARK BEWOELKT";
            else if (condition == "Cloudy" || condition == "Overcast") condition = "BEWOELKT";
            else if (condition == "Clear" || condition == "Mainly clear") condition = "KLAR";
            else if (condition == "Rain") condition = "REGEN";
            else if (condition == "Drizzle") condition = "NIESELREGEN";
            else if (condition == "Snow") condition = "SCHNEE";
            else if (condition == "Fog") condition = "NEBEL";
            condition.toUpperCase();
            drawDisplayLabel(condition, 12, y + 17, 142, TL_DATUM, 0x3DE7, FONT_LABEL);
            String range = String(day.low) + "/" + String(day.high) + "C";
            drawDisplayLabel(range, 228, y + 17, 76, TR_DATUM, 0xAFE5, FONT_LABEL);
            drawDisplayLabel("REGEN " + String(day.rainChance) + "%",
                             12, y + 32, 216, TL_DATUM, 0x3DE7, FONT_LABEL);
        } else {
            drawDisplayLabel(String(labels[slot]) + " // KEINE DATEN",
                             12, y, 216, TL_DATUM, 0x3DE7, FONT_LABEL);
        }
    }
}'''
s = replace_function(s, "void renderWeatherPage() {", "void renderMarketsPage() {", weather)

display.write_text(s, encoding="utf-8")
print("Pip-Boy V2: clean STAT, DATA and RADIO register layout applied")
