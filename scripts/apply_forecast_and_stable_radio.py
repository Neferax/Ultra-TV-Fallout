#!/usr/bin/env python3
"""Add a compact four-day Open-Meteo forecast and remove the flashing GIF fallback."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
dashboard_h = root / "src/dashboard.h"
feeds_cpp = root / "src/feeds.cpp"
gif_cpp = root / "src/gif_player.cpp"

# Fixed-size forecast storage keeps ESP8266 heap use predictable.
s = dashboard_h.read_text(encoding="utf-8")
s = s.replace(
'''struct WeatherData {
    char location[24];
    char condition[24];
    int temperature;
    int high;
    int low;
    int rainChance;
};''',
'''struct WeatherForecastDay {
    char date[6];
    char condition[16];
    int high;
    int low;
    int rainChance;
};

struct WeatherData {
    char location[24];
    char condition[24];
    int temperature;
    int high;
    int low;
    int rainChance;
    uint8_t forecastCount;
    WeatherForecastDay forecast[4];
};'''
)
dashboard_h.write_text(s, encoding="utf-8")

s = feeds_cpp.read_text(encoding="utf-8")
s = s.replace(
'''    daily["temperature_2m_max"] = true;
    daily["temperature_2m_min"] = true;
    daily["precipitation_probability_max"] = true;''',
'''    daily["time"] = true;
    daily["weather_code"] = true;
    daily["temperature_2m_max"] = true;
    daily["temperature_2m_min"] = true;
    daily["precipitation_probability_max"] = true;'''
)
s = s.replace(
'''                 "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max" +
                 "&forecast_days=1&timezone=auto";''',
'''                 "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max" +
                 "&forecast_days=4&timezone=auto";'''
)
s = s.replace(
'''    JsonArrayConst highs = daily["temperature_2m_max"].as<JsonArrayConst>();
    JsonArrayConst lows = daily["temperature_2m_min"].as<JsonArrayConst>();
    JsonArrayConst rain = daily["precipitation_probability_max"].as<JsonArrayConst>();''',
'''    JsonArrayConst dates = daily["time"].as<JsonArrayConst>();
    JsonArrayConst codes = daily["weather_code"].as<JsonArrayConst>();
    JsonArrayConst highs = daily["temperature_2m_max"].as<JsonArrayConst>();
    JsonArrayConst lows = daily["temperature_2m_min"].as<JsonArrayConst>();
    JsonArrayConst rain = daily["precipitation_probability_max"].as<JsonArrayConst>();'''
)
needle = '''    runtime.data.rainChance = rain.isNull() || rain.size() == 0
                                  ? 0
                                  : constrain(static_cast<int>(roundf(rain[0].as<float>())), 0, 100);

    runtime.hasData = true;'''
replacement = '''    runtime.data.rainChance = rain.isNull() || rain.size() == 0
                                  ? 0
                                  : constrain(static_cast<int>(roundf(rain[0].as<float>())), 0, 100);

    runtime.data.forecastCount = 0;
    size_t forecastSize = dates.size();
    if (codes.size() < forecastSize) forecastSize = codes.size();
    if (highs.size() < forecastSize) forecastSize = highs.size();
    if (lows.size() < forecastSize) forecastSize = lows.size();
    if (rain.size() < forecastSize) forecastSize = rain.size();
    if (forecastSize > 4) forecastSize = 4;
    for (size_t index = 0; index < forecastSize; ++index) {
        const char *isoDate = dates[index] | "";
        WeatherForecastDay &day = runtime.data.forecast[index];
        if (strlen(isoDate) >= 10) {
            snprintf(day.date, sizeof(day.date), "%c%c.%c%c",
                     isoDate[8], isoDate[9], isoDate[5], isoDate[6]);
        }
        copyString(day.condition, sizeof(day.condition), weatherCodeToText(codes[index] | 0));
        day.high = static_cast<int>(roundf(highs[index].as<float>()));
        day.low = static_cast<int>(roundf(lows[index].as<float>()));
        day.rainChance = constrain(static_cast<int>(roundf(rain[index].as<float>())), 0, 100);
        ++runtime.data.forecastCount;
    }

    runtime.hasData = true;'''
if needle not in s:
    raise SystemExit("Could not locate weather result parsing block")
s = s.replace(needle, replacement)
needle = '''    root["rainChance"] = weather.rainChance;
}'''
replacement = '''    root["rainChance"] = weather.rainChance;
    JsonArray forecast = root["forecast"].to<JsonArray>();
    for (uint8_t index = 0; index < weather.forecastCount && index < 4; ++index) {
        JsonObject day = forecast.add<JsonObject>();
        day["date"] = weather.forecast[index].date;
        day["condition"] = weather.forecast[index].condition;
        day["high"] = weather.forecast[index].high;
        day["low"] = weather.forecast[index].low;
        day["rainChance"] = weather.forecast[index].rainChance;
    }
}'''
if needle not in s:
    raise SystemExit("Could not locate weather JSON serialization block")
s = s.replace(needle, replacement)
feeds_cpp.write_text(s, encoding="utf-8")

# Include live feed state and each forecast day in the render-cache key.
display_cpp = root / "src/display.cpp"
s = display_cpp.read_text(encoding="utf-8")
start = s.find("void hashWeatherData(uint32_t &hash) {")
end = s.find("\nvoid hashMarketData(", start)
if start < 0 or end < 0:
    raise SystemExit("Could not locate weather render-cache hash")
hash_function = r'''void hashWeatherData(uint32_t &hash) {
    hashValue(hash, feedsWeatherSource());
    hashValue(hash, feedsWeatherUsesFahrenheit());
    hashValue(hash, weatherWaitingForSync());
    hashValue(hash, feedRuntime.weather.syncing);
    hashCString(hash, feedRuntime.weather.lastError);

    const WeatherData *weather = effectiveWeatherData();
    bool hasData = weather != nullptr;
    hashValue(hash, hasData);
    if (!hasData) return;

    hashCString(hash, weather->location);
    hashCString(hash, weather->condition);
    hashValue(hash, weather->temperature);
    hashValue(hash, weather->high);
    hashValue(hash, weather->low);
    hashValue(hash, weather->rainChance);
    hashValue(hash, weather->forecastCount);
    for (uint8_t index = 0; index < weather->forecastCount && index < 4; ++index) {
        hashCString(hash, weather->forecast[index].date);
        hashCString(hash, weather->forecast[index].condition);
        hashValue(hash, weather->forecast[index].high);
        hashValue(hash, weather->forecast[index].low);
        hashValue(hash, weather->forecast[index].rainChance);
    }
}'''
s = s[:start] + hash_function + s[end:]
display_cpp.write_text(s, encoding="utf-8")

# A failed/unsupported GIF now leaves the stable archive page visible.
s = gif_cpp.read_text(encoding="utf-8")
s = s.replace("bool fallbackAnimationActive = false;\nuint32_t fallbackFrameAtMs = 0;\n", "")
start = s.find("    if (fallbackAnimationActive && decoder == nullptr && targetDisplay != nullptr) {")
if start >= 0:
    end = s.find("    if (decoder == nullptr) return false;", start)
    if end < 0:
        raise SystemExit("GIF fallback block end not found")
    s = s[:start] + s[end:]
s = s.replace('''        if (display != nullptr) {
            targetDisplay = display;
            fallbackAnimationActive = true;
            fallbackFrameAtMs = 0;
        }
        return false;''', '''        (void)display;
        return false;''')
s = s.replace("    fallbackAnimationActive = false;\n    fallbackFrameAtMs = 0;\n", "")
s = s.replace("    return decoder != nullptr || fallbackAnimationActive;", "    return decoder != nullptr;")
s = s.replace('''    if (gifPathCount == 0) {
        targetDisplay = &display;
        fallbackAnimationActive = true;
        fallbackFrameAtMs = 0;
        gifStartedAtMs = millis();
        return true;
    }''', '''    if (gifPathCount == 0) return false;''')
s = s.replace('''    // An incompatible or damaged album entry must not leave RADIO blank.
    targetDisplay = &display;
    fallbackAnimationActive = true;
    fallbackFrameAtMs = 0;
    gifStartedAtMs = millis();
    return true;''', '''    // Leave the stable archive page visible if this GIF cannot be decoded.
    return false;''')
gif_cpp.write_text(s, encoding="utf-8")

print("Four-day weather forecast and stable non-flashing GIF failure handling applied")
