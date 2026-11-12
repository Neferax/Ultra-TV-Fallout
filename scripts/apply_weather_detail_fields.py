#!/usr/bin/env python3
"""Add current-condition detail fields from Open-Meteo for the Pip-Boy DATA page."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
dashboard_h = root / "src/dashboard.h"
feeds_cpp = root / "src/feeds.cpp"

s = dashboard_h.read_text(encoding="utf-8")
s = s.replace(
'''struct WeatherData {
    char location[24];
    char condition[24];
    int temperature;
    int high;
    int low;
    int rainChance;
    uint8_t forecastCount;
    WeatherForecastDay forecast[4];
};''',
'''struct WeatherData {
    char location[24];
    char condition[24];
    int temperature;
    int high;
    int low;
    int rainChance;
    int feelsLike;
    int humidity;
    int precipitation;
    int windSpeed;
    int windDirection;
    int windGusts;
    int uvIndex;
    char sunrise[6];
    char sunset[6];
    uint8_t forecastCount;
    WeatherForecastDay forecast[4];
};'''
)
if "int feelsLike;" not in s:
    raise SystemExit("WeatherData structure extension failed")
dashboard_h.write_text(s, encoding="utf-8")

s = feeds_cpp.read_text(encoding="utf-8")
s = s.replace(
'''    current["temperature_2m"] = true;
    current["weather_code"] = true;

    JsonObject daily = filter["daily"].to<JsonObject>();
    daily["temperature_2m_max"] = true;''',
'''    current["temperature_2m"] = true;
    current["apparent_temperature"] = true;
    current["relative_humidity_2m"] = true;
    current["precipitation"] = true;
    current["wind_speed_10m"] = true;
    current["wind_direction_10m"] = true;
    current["wind_gusts_10m"] = true;
    current["uv_index"] = true;
    current["weather_code"] = true;

    JsonObject daily = filter["daily"].to<JsonObject>();
    daily["sunrise"] = true;
    daily["sunset"] = true;
    daily["temperature_2m_max"] = true;'''
)
s = s.replace(
'''                 "&current=temperature_2m,weather_code" +
                 "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max" +''',
'''                 "&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,wind_gusts_10m,uv_index,weather_code" +
                 "&daily=sunrise,sunset,weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max" +'''
)
needle = '''    runtime.data.rainChance = rain.isNull() || rain.size() == 0
                                  ? 0
                                  : constrain(static_cast<int>(roundf(rain[0].as<float>())), 0, 100);

    runtime.data.forecastCount = 0;'''
replacement = '''    runtime.data.rainChance = rain.isNull() || rain.size() == 0
                                  ? 0
                                  : constrain(static_cast<int>(roundf(rain[0].as<float>())), 0, 100);
    runtime.data.feelsLike = current["apparent_temperature"] | runtime.data.temperature;
    runtime.data.humidity = current["relative_humidity_2m"] | 0;
    runtime.data.precipitation = static_cast<int>(roundf((current["precipitation"] | 0.0f) * 10.0f));
    runtime.data.windSpeed = static_cast<int>(roundf(current["wind_speed_10m"] | 0.0f));
    runtime.data.windDirection = constrain(static_cast<int>(roundf(current["wind_direction_10m"] | 0.0f)), 0, 359);
    runtime.data.windGusts = static_cast<int>(roundf(current["wind_gusts_10m"] | 0.0f));
    runtime.data.uvIndex = static_cast<int>(roundf(current["uv_index"] | 0.0f));
    const char *sunrise = daily["sunrise"][0] | "";
    const char *sunset = daily["sunset"][0] | "";
    if (strlen(sunrise) >= 16) snprintf(runtime.data.sunrise, sizeof(runtime.data.sunrise), "%c%c:%c%c", sunrise[11], sunrise[12], sunrise[14], sunrise[15]);
    if (strlen(sunset) >= 16) snprintf(runtime.data.sunset, sizeof(runtime.data.sunset), "%c%c:%c%c", sunset[11], sunset[12], sunset[14], sunset[15]);

    runtime.data.forecastCount = 0;'''
if needle not in s:
    raise SystemExit("Could not locate weather current-data parsing insertion")
s = s.replace(needle, replacement)
needle = '''    root["rainChance"] = weather.rainChance;
    JsonArray forecast = root["forecast"].to<JsonArray>();'''
replacement = '''    root["rainChance"] = weather.rainChance;
    root["feelsLike"] = weather.feelsLike;
    root["humidity"] = weather.humidity;
    root["precipitation"] = weather.precipitation;
    root["windSpeed"] = weather.windSpeed;
    root["windDirection"] = weather.windDirection;
    root["windGusts"] = weather.windGusts;
    root["uvIndex"] = weather.uvIndex;
    root["sunrise"] = weather.sunrise;
    root["sunset"] = weather.sunset;
    JsonArray forecast = root["forecast"].to<JsonArray>();'''
if needle not in s:
    raise SystemExit("Could not locate weather JSON insertion")
s = s.replace(needle, replacement)
feeds_cpp.write_text(s, encoding="utf-8")

# Keep the weather details and the 12-second internal DATA page phase in the
# render-cache key so the two DATA views alternate without changing registers.
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
    hashValue(hash, (millis() / 12000UL) % 2UL);
    if (!hasData) return;
    hashCString(hash, weather->location);
    hashCString(hash, weather->condition);
    hashValue(hash, weather->temperature);
    hashValue(hash, weather->feelsLike);
    hashValue(hash, weather->humidity);
    hashValue(hash, weather->precipitation);
    hashValue(hash, weather->windSpeed);
    hashValue(hash, weather->windDirection);
    hashValue(hash, weather->windGusts);
    hashValue(hash, weather->uvIndex);
    hashCString(hash, weather->sunrise);
    hashCString(hash, weather->sunset);
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
print("Open-Meteo weather detail fields and timed DATA view cache added")
