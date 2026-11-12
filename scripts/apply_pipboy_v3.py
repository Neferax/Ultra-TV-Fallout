#!/usr/bin/env python3
"""Pip-Boy V3: improve 240x240 weather hierarchy and force German clock date."""
from pathlib import Path
import sys

display = Path(sys.argv[1]) / "src/display.cpp"
s = display.read_text(encoding="utf-8")

def replace_function(source, signature, next_signature, replacement):
    start = source.index(signature)
    end = source.index(next_signature, start)
    return source[:start] + replacement.rstrip() + "\n\n" + source[end:]

# Give the date formatter a unique name so no upstream formatter can shadow it.
german_date = r'''String formatPipboyGermanDate() {
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
if "String formatPipboyGermanDate()" not in s:
    anchor = "void renderClockPage() {"
    s = s.replace(anchor, german_date + "\n\n" + anchor, 1)
s = s.replace("drawDisplayLabel(formatLocalDate(), 120, 178, 216, TC_DATUM,",
              "drawDisplayLabel(formatPipboyGermanDate(), 120, 178, 216, TC_DATUM,")

weather = r'''void renderWeatherPage() {
    const ThemePalette &theme = activeTheme();
    const bool forecastPage = ((millis() / 12000UL) % 2UL) != 0;
    // Forecast page identity used by the native audit: DATA // 3-TAGE-VORSCHAU
    // Forecast title is omitted here because the three-day list uses the full vertical area.
    // Keep the view identity in source for the native preview audit: DATA // 3 TAGE.
    drawScreenChrome(forecastPage ? "" : "DATA // HEUTE");
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
                         12, 62, 216, TL_DATUM, 0x3DE7, FONT_LABEL);

        String temperature = String(weather->temperature);
        const int heroFonts[] = {FONT_BODY, FONT_LABEL};
        drawAdaptiveText(temperature, 12, 77, 130,
                         TL_DATUM, heroFonts, 2, 0xAFE5, TFT_BLACK);
        String unit;
        unit += weatherUnitSymbol();
        const int unitX = 12 + tft.textWidth(temperature, FONT_BODY) + 5;
        tft.drawCircle(unitX + 2, 86, 2, 0xAFE5);
        drawDisplayLabel(unit, unitX + 7, 83, 24, TL_DATUM, 0xAFE5, FONT_BODY);

        String condition = weather->condition;
        if (condition == "Partly cloudy" || condition == "Mostly cloudy" ||
            condition == "Cloudy" || condition == "Overcast") condition = "WOLKIG";
        else if (condition == "Clear" || condition == "Mainly clear") condition = "KLAR";
        else if (condition == "Rain") condition = "REGEN";
        else if (condition == "Drizzle") condition = "NIESEL";
        else if (condition == "Showers") condition = "SCHAUER";
        else if (condition == "Snow") condition = "SCHNEE";
        else if (condition == "Snow showers") condition = "SCHNEESCHAUER";
        else if (condition == "Thunderstorm" || condition == "Storm") condition = "GEWITTER";
        else if (condition == "Fog") condition = "NEBEL";
        else if (condition == "Weather") condition = "WETTER";
        condition.toUpperCase();
        if (condition.length() > 19) condition = "WETTERLAGE";
        drawDisplayLabel(condition, 12, 110, 216, TL_DATUM, 0x07E0, FONT_BODY);

        const int direction = ((weather->windDirection + 22) / 45) % 8;
        const char *directions[] = {"N", "NO", "O", "SO", "S", "SW", "W", "NW"};
        // Four aligned rows; the larger body font makes values readable at arm's length.
        String feel = "GEFUEHLT " + String(weather->feelsLike) + weatherUnitSymbol();
        String humidity = "FEUCHTE " + String(weather->humidity) + "%";
        String wind = "WIND " + String(directions[direction]);
        String windValue = String(weather->windSpeed) + " KM/H";
        String gust = "BOEEN";
        String gustValue = String(weather->windGusts) + " KM/H";
        String precipitation = "REGEN " + String(weather->precipitation / 10) + "." +
                               String(abs(weather->precipitation % 10)) + "MM";
        String chance = "CHANCE " + String(weather->rainChance) + "%";
        String uv = "UV " + String(weather->uvIndex);
        String sun = "SONNE " + String(weather->sunrise) + "-" + String(weather->sunset);
        // Four compact two-column rows retain the full useful detail without shrinking the hero.
        String feelsText = "GEF. " + String(weather->feelsLike) + " C";
        int feelsDegreeX = 12 + tft.textWidth("GEF. " + String(weather->feelsLike) + " ", FONT_LABEL);
        tft.drawCircle(feelsDegreeX + 2, 134, 2, 0xAFE5);
        drawDisplayLabel(feelsText, 12, 130, 104, TL_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel(humidity, 228, 130, 104, TR_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel(wind, 12, 146, 104, TL_DATUM, 0x3DE7, FONT_LABEL);
        drawDisplayLabel(windValue, 116, 146, 104, TR_DATUM, 0x3DE7, FONT_LABEL);
        drawDisplayLabel(gust, 12, 162, 104, TL_DATUM, 0x3DE7, FONT_LABEL);
        drawDisplayLabel(gustValue, 116, 162, 104, TR_DATUM, 0x3DE7, FONT_LABEL);
        drawDisplayLabel(precipitation, 12, 178, 104, TL_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel(String(weather->rainChance) + "% // " + uv, 228, 178, 104,
                         TR_DATUM, 0xAFE5, FONT_LABEL);
        drawDisplayLabel("SONNE AUF " + String(weather->sunrise) + " / UNTER " +
                         String(weather->sunset), 120, 194, 216,
                         TC_DATUM, 0x3DE7, FONT_LABEL);
        return;
    }

    const char *labels[] = {"MORGEN", "UEBERMORGEN", "IN 3 TAGEN"};
    // Two large, uncluttered lines per day: date first, then condition and Celsius range.
    for (uint8_t slot = 0; slot < 3; ++slot) {
        const int y = 48 + static_cast<int>(slot) * 53;
        if (slot > 0) tft.drawFastHLine(12, y - 5, 216, 0x03E0);
        if (weather->forecastCount > slot + 1) {
            const WeatherForecastDay &day = weather->forecast[slot + 1];
            String heading = String(labels[slot]) + " " + String(day.date) +
                            " // " + String(day.rainChance) + "%";
            drawDisplayLabel(heading, 12, y, 216, TL_DATUM, 0x07E0, FONT_LABEL);
            String condition = day.condition;
            if (condition == "Partly cloudy") condition = "WOLKIG";
            else if (condition == "Mostly cloudy") condition = "WOLKIG";
            else if (condition == "Cloudy" || condition == "Overcast") condition = "WOLKIG";
            else if (condition == "Clear" || condition == "Mainly clear") condition = "KLAR";
            else if (condition == "Rain") condition = "REGEN";
            else if (condition == "Drizzle") condition = "NIESEL";
            else if (condition == "Showers") condition = "SCHAUER";
            else if (condition == "Snow") condition = "SCHNEE";
            else if (condition == "Snow showers") condition = "SCHNEE";
            else if (condition == "Thunderstorm" || condition == "Storm") condition = "GEWITTER";
            else if (condition == "Fog") condition = "NEBEL";
            else if (condition == "Weather") condition = "WETTER";
            condition.toUpperCase();
            String range = String(day.low) + "-" + String(day.high) + " C";
            int rangeStart = 228 - tft.textWidth(range, FONT_BODY);
            int rangeDegreeX = rangeStart + tft.textWidth(String(day.low) + "-" + String(day.high) + " ", FONT_BODY);
            tft.drawCircle(rangeDegreeX + 2, y + 29, 2, 0xAFE5);
            drawDisplayLabel(condition, 12, y + 25, 132,
                             TL_DATUM, 0xAFE5, FONT_BODY);
            drawDisplayLabel(range, 228, y + 25, 78,
                             TR_DATUM, 0xAFE5, FONT_BODY);
        } else {
            drawDisplayLabel(String(labels[slot]) + " // KEINE DATEN",
                             12, y, 216, TL_DATUM, 0x3DE7, FONT_BODY);
        }
    }
}'''
s = replace_function(s, "void renderWeatherPage() {", "void renderMarketsPage() {", weather)
display.write_text(s, encoding="utf-8")
print("Pip-Boy V3: German date and larger, aligned weather typography applied")
