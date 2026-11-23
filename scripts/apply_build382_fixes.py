#!/usr/bin/env python3
"""Build 382: fix weather text collisions and make RADIO animated when GIF playback fails."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
display=root/"src/display.cpp"
gif=root/"src/gif_player.cpp"
def replace_function(s, start, end, replacement):
    a=s.index(start); b=s.index(end,a)
    return s[:a]+replacement.rstrip()+"\n\n"+s[b:]
s=display.read_text(encoding="utf-8")
weather=r'''void renderWeatherPage() {
    const ThemePalette &theme = activeTheme();
    const bool forecastPage = ((millis() / 12000UL) % 2UL) != 0;
    drawScreenChrome(forecastPage ? "DATA // 3 TAGE" : "DATA // HEUTE");
    if (!hasWeatherContent()) {
        tft.drawRect(12, 72, 216, 118, theme.accent);
        drawDisplayLabel("WETTERDATEN", 120, 90, 200, TC_DATUM, theme.text, FONT_LABEL);
        drawDisplayLabel(feedRuntime.weather.syncing ? "VERBINDUNG..." :
            feedRuntime.weather.lastError[0] ? "KEINE DATEN" : "WARTE AUF DATEN",
            120, 128, 200, TC_DATUM, theme.muted, FONT_LABEL);
        drawDisplayLabel("OPEN-METEO // 47239", 120, 166, 200, TC_DATUM, theme.muted, FONT_INFO);
        return;
    }
    const WeatherData *weather = effectiveWeatherData();
    if (!forecastPage) {
        drawDisplayLabel(weather->location[0] ? weather->location : "DUISBURG // 47239",
                        12, 63, 216, TL_DATUM, theme.muted, FONT_LABEL);
        const int tempFonts[] = {FONT_HUGE, FONT_TITLE, FONT_BODY, FONT_LABEL};
        drawAdaptiveText(formatWeatherTemperature(weather->temperature), 12, 78, 130,
                        TL_DATUM, tempFonts, 4, theme.text, TFT_BLACK);
        String condition=weather->condition; condition.toLowerCase();
        if(condition.indexOf("partly")>=0) condition="TEILWOLKIG";
        else if(condition.indexOf("cloud")>=0||condition.indexOf("overcast")>=0) condition="BEWOELKT";
        else if(condition.indexOf("clear")>=0) condition="KLAR";
        else if(condition.indexOf("rain")>=0||condition.indexOf("shower")>=0) condition="REGEN";
        else if(condition.indexOf("drizzle")>=0) condition="NIESEL";
        else if(condition.indexOf("snow")>=0) condition="SCHNEE";
        else if(condition.indexOf("thunder")>=0||condition.indexOf("storm")>=0) condition="GEWITTER";
        else if(condition.indexOf("fog")>=0) condition="NEBEL";
        condition.toUpperCase(); if(condition.length()>15) condition="WETTERLAGE";
        drawDisplayLabel(condition, 12, 112, 216, TL_DATUM, theme.accent, FONT_BODY);
        const int d=((weather->windDirection+22)/45)%8;
        const char *dirs[]={"N","NO","O","SO","S","SW","W","NW"};
        drawDisplayLabel("GEF. "+String(weather->feelsLike)+" C",12,133,108,TL_DATUM,theme.text,FONT_LABEL);
        drawDisplayLabel("FEUCHTE "+String(weather->humidity)+"%",228,133,108,TR_DATUM,theme.text,FONT_LABEL);
        drawDisplayLabel("WIND "+String(dirs[d])+" "+String(weather->windSpeed)+" KM/H",12,151,108,TL_DATUM,theme.muted,FONT_LABEL);
        drawDisplayLabel("BOEEN "+String(weather->windGusts)+" KM/H",228,151,108,TR_DATUM,theme.muted,FONT_LABEL);
        drawDisplayLabel("REGEN "+String(weather->precipitation/10)+"."+String(abs(weather->precipitation%10))+" MM",12,169,108,TL_DATUM,theme.text,FONT_LABEL);
        drawDisplayLabel("CHANCE "+String(weather->rainChance)+"%",228,169,108,TR_DATUM,theme.text,FONT_LABEL);
        drawDisplayLabel("UV "+String(weather->uvIndex),12,187,70,TL_DATUM,theme.muted,FONT_LABEL);
        drawDisplayLabel("SONNE "+String(weather->sunrise)+"/"+String(weather->sunset),228,187,140,TR_DATUM,theme.muted,FONT_LABEL);
        return;
    }
    const char *labels[]={"MORGEN","UEBERMORGEN","IN 3 TAGEN"};
    for(uint8_t slot=0;slot<3;slot++) {
        const int y=68+static_cast<int>(slot)*48;
        if(slot>0) tft.drawFastHLine(12,y-4,216,theme.accentSoft);
        if(weather->forecastCount>slot+1) {
            const WeatherForecastDay &day=weather->forecast[slot+1];
            drawDisplayLabel(String(labels[slot])+" // "+String(day.date)+" // "+String(day.rainChance)+"%",
                12,y,216,TL_DATUM,theme.accent,FONT_LABEL);
            String c=day.condition; c.toLowerCase();
            if(c.indexOf("partly")>=0)c="TEILWOLKIG";
            else if(c.indexOf("cloud")>=0||c.indexOf("overcast")>=0)c="BEWOELKT";
            else if(c.indexOf("clear")>=0)c="KLAR";
            else if(c.indexOf("rain")>=0||c.indexOf("shower")>=0)c="REGEN";
            else if(c.indexOf("drizzle")>=0)c="NIESEL";
            else if(c.indexOf("snow")>=0)c="SCHNEE";
            else if(c.indexOf("thunder")>=0||c.indexOf("storm")>=0)c="GEWITTER";
            else if(c.indexOf("fog")>=0)c="NEBEL";
            c.toUpperCase();
            drawDisplayLabel(c,12,y+16,138,TL_DATUM,theme.text,FONT_BODY);
            drawDisplayLabel(String(day.low)+"-"+String(day.high)+" C",228,y+16,82,TR_DATUM,theme.text,FONT_BODY);
            drawDisplayLabel("REGEN "+String(day.rainChance)+"%",12,y+32,216,TL_DATUM,theme.muted,FONT_LABEL);
        } else drawDisplayLabel(String(labels[slot])+" // KEINE DATEN",12,y+8,216,TL_DATUM,theme.muted,FONT_LABEL);
    }
}'''
s=replace_function(s,"void renderWeatherPage() {","void renderMarketsPage() {",weather)
display.write_text(s,encoding="utf-8")
s=gif.read_text(encoding="utf-8")
if "bool fallbackAnimationActive = false;" not in s:
    s=s.replace("uint32_t gifStartedAtMs = 0;","uint32_t gifStartedAtMs = 0;\nbool fallbackAnimationActive = false;\nbool fallbackSceneDrawn = false;\nuint32_t fallbackFrameAtMs = 0;\nint16_t fallbackScanY = 87;",1)
tick=r'''bool gifPlayerTick(uint32_t nowMs) {
    if(fallbackAnimationActive && decoder==nullptr && targetDisplay!=nullptr) {
        if(nowMs-gifStartedAtMs>=20000UL) {
            TFT_eSPI *d=targetDisplay; gifPlayerStop(); if(d) gifPlayerStartNext(*d); return true;
        }
        if(!fallbackSceneDrawn) {
            targetDisplay->fillRect(68,76,104,104,TFT_BLACK);
            targetDisplay->drawRect(68,76,104,104,0x03E0);
            targetDisplay->drawRoundRect(94,88,52,82,10,0x07E0);
            targetDisplay->fillRoundRect(98,92,44,74,8,0x0100);
            targetDisplay->drawFastHLine(104,99,32,0x07E0);
            targetDisplay->drawRect(104,105,32,8,0x03E0);
            targetDisplay->drawRoundRect(104,118,32,24,4,0x07E0);
            targetDisplay->fillRect(108,124,9,5,0xAFE5); targetDisplay->fillRect(123,124,9,5,0xAFE5);
            targetDisplay->drawFastHLine(110,147,20,0x07E0);
            targetDisplay->setTextDatum(TC_DATUM); targetDisplay->setTextFont(1); targetDisplay->setTextColor(0x07E0,TFT_BLACK);
            targetDisplay->drawString("ROBCO // RADIO",120,79,1); targetDisplay->drawString("GIF UNAVAILABLE",120,164,1);
            fallbackScanY=87; fallbackSceneDrawn=true; fallbackFrameAtMs=nowMs;
        }
        if(nowMs-fallbackFrameAtMs>=100UL) {
            fallbackFrameAtMs=nowMs; targetDisplay->drawFastHLine(76,fallbackScanY,88,TFT_BLACK);
            fallbackScanY+=3; if(fallbackScanY>168)fallbackScanY=87;
            targetDisplay->drawFastHLine(76,fallbackScanY,88,0x03E0);
        }
        yield(); return true;
    }
    if(decoder==nullptr)return false;
    if(nowMs-gifStartedAtMs>=20000UL) {
        TFT_eSPI *d=targetDisplay; gifPlayerStop(); if(d)gifPlayerStartNext(*d); return true;
    }
    if(static_cast<int32_t>(nowMs-nextFrameAtMs)<0)return false;
    int delayMs=100; const int result=decoder->playFrame(false,&delayMs,nullptr);
    if(result<0||unsupportedFrame) {
        Serial.printf("GIF decode error=%d unsupported=%u\n",result,unsupportedFrame?1U:0U);
        if(currentGifIndex<gifPathCount)rejectedGifPaths[currentGifIndex]=true;
        TFT_eSPI *d=targetDisplay; gifPlayerStop();
        if(d){targetDisplay=d;fallbackAnimationActive=true;fallbackSceneDrawn=false;gifStartedAtMs=nowMs;}
        return true;
    }
    if(result==0)decoder->reset();
    if(delayMs<20)delayMs=20; if(delayMs>5000)delayMs=5000;
    nextFrameAtMs=nowMs+static_cast<uint32_t>(delayMs); yield(); return true;
}'''
s=replace_function(s,"bool gifPlayerTick(uint32_t nowMs) {","void gifPlayerStop() {",tick)
start=r'''bool gifPlayerStartNext(TFT_eSPI &display) {
    if(gifFileListDirty)gifPlayerRefreshFiles();
    if(gifPathCount==0) {
        targetDisplay=&display;fallbackAnimationActive=true;fallbackSceneDrawn=false;gifStartedAtMs=millis();fallbackFrameAtMs=0;return true;
    }
    for(uint8_t attempt=0;attempt<gifPathCount;attempt++) {
        const uint8_t selected=nextGifIndex; nextGifIndex=static_cast<uint8_t>((nextGifIndex+1)%gifPathCount);
        if(rejectedGifPaths[selected])continue;
        if(gifPlayerStart(gifPaths[selected],display)){currentGifIndex=selected;Serial.printf("GIF started: %s\n",gifPaths[selected]);return true;}
        rejectedGifPaths[selected]=true;
    }
    memset(rejectedGifPaths,0,sizeof(rejectedGifPaths));
    targetDisplay=&display;fallbackAnimationActive=true;fallbackSceneDrawn=false;gifStartedAtMs=millis();fallbackFrameAtMs=0;
    Serial.println(F("GIF archive failed; animated fallback active"));return true;
}'''
s=replace_function(s,"bool gifPlayerStartNext(TFT_eSPI &display) {","bool gifPlayerUploadStart(",start)
s=s.replace("    targetDisplay = nullptr;\n","    targetDisplay = nullptr;\n    fallbackAnimationActive = false;\n    fallbackSceneDrawn = false;\n    fallbackFrameAtMs = 0;\n",1)
s=s.replace("    return decoder != nullptr;","    return decoder != nullptr || fallbackAnimationActive;",1)
gif.write_text(s,encoding="utf-8")
assert "DATA // 3 TAGE" in weather
print("Build382 correction script applied: weather collision cleanup + RADIO fallback")
