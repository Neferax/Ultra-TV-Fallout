# Implementierungsstatus – 10.11.2026

## Gerät und Ziel
- GeekMagic SmallTV Ultra, Stock-Firmware `Ultra-V9.0.50`
- Geräte-IP bei der letzten Auslesung: `192.168.178.70`
- Stock-GIFs und Dateigrößen wurden read-only dokumentiert; keine Datei wurde auf dem Gerät verändert.
- Ziel: Uhr- und Wetterseite sowie GIF-Anzeigen in einem durchgängigen Fallout-4-/Pip-Boy-/RobCo-Stil. GIF-Seite direkt nach Wetter, keine unnötigen Zusatzseiten.

## Firmware-Basis und Uhr-/Wetterdesign
- Als Quellbasis dient [iodn/geekmagic-tv-esp8266](https://github.com/iodn/geekmagic-tv-esp8266), das SmallTV Ultra / ESP8266 ausdrücklich unterstützt.
- `patches/0001-fallout-pipboy-renderers.patch` gestaltet Uhr und Wetter mit RobCo-/Vault-Tec-Panels neu. NTP- und Open-Meteo-Datenpfade bleiben erhalten.
- Ausgangsblob des Upstream-`src/display.cpp`: `ef482ea3cc556eb414fff6178fcc7a4d136563a9`.
- Terminal-Farbpalette (Theme-ID 2) ist als Ausgangsbasis dokumentiert.
- Der Renderer-Patch wurde noch nicht lokal mit `git apply` oder einem Compiler validiert.

## GIF-Player und Album
- AnimatedGIF wurde mit Apache-2.0-Lizenz lokal unter `lib/AnimatedGIF/` vendort.
- Konfiguration: `MAX_CODE_SIZE=11`, `MAX_WIDTH=240`. Der Compile-Probe erzwingt `sizeof(AnimatedGIF) <= 15360` Bytes.
- `firmware/gif_player.cpp/.h` implementiert LittleFS-Datei-Callbacks, RAW-Scanline-Dekodierung und RGB565-Ausgabe direkt über TFT_eSPI. Es wird kein 240×240-RGB565-Vollbildpuffer angelegt.
- Decoder-Instanz wird bei Bedarf im sekundären IRAM-Heap angelegt und vor Feed-/TLS-Arbeit, OTA und anstehenden Netzwerkaktionen wieder freigegeben.
- Vor dem Start prüft der Player `free` und `largestBlock` des IRAM-Heaps gegen `sizeof(AnimatedGIF)+2048`. Bei zu wenig Speicher wird die GIF-Wiedergabe übersprungen, nicht auf DRAM ausgewichen.
- `patches/0002-gif-player-integration.patch` verwendet den vorhandenen Status-Seitenslot für die GIF-Seite direkt nach Weather; die Gesamtzahl der Dashboard-Seiten wird nicht erhöht. Als Standard sind ausschließlich Clock, Weather und GIF aktiviert; das Terminal-Theme, 20 Sekunden Seitenwechsel und Open-Meteo-Wetter für PLZ 47239 Duisburg sind voreingestellt. Seitenkonfiguration und geschützter Upload unter `/gif` mit `POST /gif/upload` sind ergänzt.
- Uploads prüfen GIF-Signatur und 240×240-Canvas, schreiben zunächst in eine temporäre Datei und ersetzen erst nach erfolgreichem Abschluss. Bis zu zwölf alphabetisch sortierte Dateien werden abgespielt; der Player wechselt nach 20 Sekunden zur nächsten.
- Einschränkungen: maximal 300 KiB pro Datei, maximal zwölf Dateien, LZW-Codegröße höchstens 11 Bit, nur vollständig deckende Vollbild-Frames. Transparente und partielle Frames werden abgewiesen, weil kein Compositing-Framebuffer verfügbar ist.
- Stock-GIFs werden beim Firmwarewechsel nicht automatisch migriert. Originale müssen außerhalb des Geräts gesichert und nach Installation über `/gif` erneut hochgeladen werden. Die vorhandenen Dateien wurden noch nicht auf LZW-/Frame-Kompatibilität geprüft.

## Reproduzierbarer Build
- GitHub-Actions-Workflow: [smalltv-firmware-build.yml](../.github/workflows/smalltv-firmware-build.yml).
- Er checkt den erwarteten Upstream-Quellstand aus, wendet beide Patches an, kopiert die lokale Decoderbibliothek und den Player hinein und baut mit `pio run -e nodemcuv2`.
- Bei Erfolg wird `firmware.bin` als 14 Tage verfügbares Actions-Artefakt abgelegt.
- Die verfügbaren GitHub-Abfragen liefern bislang keine bestätigten Workflow-Checks. Deshalb sind Patch-Anwendung, Compile-Erfolg, tatsächliche Instanzgröße, IRAM-Allokation und Binärgröße **noch nicht verifiziert**.

## Was noch offen ist
1. GitHub-Actions-Build tatsächlich erfolgreich durchlaufen lassen und Fehler korrigieren.
2. Auf dem Build die echte Decoder-Instanzgröße und IRAM-Reserve protokollieren.
3. Geeignete GIFs testen: 11-Bit-LZW, vollständig deckende Frames, keine Transparenz oder Disposal-Methode 2.
4. Laufzeit prüfen: Framerate, Seitenwechsel, TLS-Feed, OTA, Watchdog und Speicherfragmentierung.
5. Backup-/Restore- und Recovery-Weg für genau diese Hardware-/Partitionsvariante prüfen.

## Sicherheit und Gerätestatus
- Keine Firmware wurde geflasht.
- Keine Stock-GIFs, Einstellungen oder Dateien wurden gelöscht oder überschrieben.
- Es gibt noch kein nachweislich flashfertiges Firmware-Image.
- Der Build-/Laufzeitstatus wird nicht als erfolgreich bezeichnet, bevor die Tests tatsächlich vorliegen.
