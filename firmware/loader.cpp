#ifdef LOADER_BUILD
// Minimal OTA trampoline for GeekMagic SmallTV Ultra (ESP8266).
// Install this small image through the stock /update page. It starts an
// isolated Wi-Fi AP and exposes the ESP8266 HTTP OTA updater at /update.
// The loader is compiled with the same 4 MB / OTA-capable layout as the
// Fallout application image, so the second upload has enough sketch space.

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPUpdateServer.h>

static ESP8266WebServer server(80);
static ESP8266HTTPUpdateServer updater;

void setup() {
    Serial.begin(115200);
    Serial.println();
    Serial.println(F("ROBCO // FALLOUT OTA LOADER"));

    WiFi.persistent(false);
    WiFi.disconnect(true);
    delay(100);

    WiFi.mode(WIFI_AP);
    WiFi.softAP("SmallTV-Loader");

    Serial.print(F("Loader AP: "));
    Serial.println(WiFi.softAPIP());

    updater.setup(&server);
    server.begin();
    Serial.println(F("Open http://192.168.4.1/update"));
}

void loop() {
    server.handleClient();
    yield();
}
#endif  // LOADER_BUILD
