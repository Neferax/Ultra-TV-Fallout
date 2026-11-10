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
- Beide Renderer-/Integrationspatches wurden im GitHub-Actions-Lauf erfolgreich angewendet; der anschließende PlatformIO-Build war erfolgreich.

## GIF-Player und Album
- AnimatedGIF wurde mit Apache-2.0-Lizenz lokal unter `lib/AnimatedGIF/` vendort.
- Konfiguration: `MAX_CODE_SIZE=11`, `MAX_WIDTH=240`. Der Compile-Probe erzwingt `sizeof(AnimatedGIF) <= 15360` Bytes.
- `firmware/gif_player.cpp/.h` implementiert LittleFS-Datei-Callbacks, RAW-Scanline-Dekodierung und RGB565-Ausgabe direkt über TFT_eSPI. Es wird kein 240×240-RGB565-Vollbildpuffer angelegt.
- Decoder-Instanz wird bei Bedarf im sekundären IRAM-Heap angelegt und vor Feed-/TLS-Arbeit, OTA und anstehenden Netzwerkaktionen wieder freigegeben.
- Vor dem Start prüft der Player `free` und `largestBlock` des IRAM-Heaps gegen `sizeof(AnimatedGIF)+2048`. Bei zu wenig Speicher wird die GIF-Wiedergabe übersprungen, nicht auf DRAM ausgewichen.
- `patches/0002-gif-player-integration.patch` verwendet den vorhandenen Status-Seitenslot für die GIF-Seite direkt nach Weather; die Gesamtzahl der Dashboard-Seiten wird nicht erhöht. Als Standard sind ausschließlich Clock, Weather und GIF aktiviert; das Terminal-Theme, 20 Sekunden Seitenwechsel, Europe/Berlin mit automatischer Sommerzeit und Open-Meteo-Wetter für PLZ 47239 Duisburg sind voreingestellt. Seitenkonfiguration und geschützter Upload unter `/gif` mit `POST /gif/upload` sind ergänzt.
- Uploads prüfen GIF-Signatur und 240×240-Canvas, schreiben zunächst in eine temporäre Datei und ersetzen erst nach erfolgreichem Abschluss. Zusätzlich wird vor jedem Schreibblock der freie LittleFS-Speicher geprüft; mindestens 4 KiB Reserve bleiben für Dateisystem-Metadaten und den Abschluss des Uploads. Bis zu zwölf alphabetisch sortierte Dateien werden abgespielt; der Player wechselt nach 20 Sekunden zur nächsten.
- GIF-Schleife: Der Player wertet das Ende eines Durchlaufs aus und setzt den Decoder direkt auf Dateianfang zurück, statt mögliche Trailer-Bytes als weiteres Frame zu interpretieren.
- Einschränkungen: maximal 300 KiB pro Datei, maximal zwölf Dateien, LZW-Codegröße höchstens 11 Bit, nur Vollbild-Frames; transparente Pixel werden schwarz dargestellt, partielle Frames werden abgewiesen. Alle Farben werden in Pip-Boy-Grün umgerechnet.
- Stock-GIFs werden beim Firmwarewechsel nicht automatisch migriert. Originale müssen außerhalb des Geräts gesichert und nach Installation über `/gif` erneut hochgeladen werden. Die vorhandenen Dateien wurden noch nicht auf LZW-/Frame-Kompatibilität geprüft. Auch die Übernahme der WLAN-Zugangsdaten ist nicht bestätigt; gegebenenfalls muss das Failsafe-AP der neuen Firmware zur WLAN-Einrichtung verwendet werden.

## Reproduzierbarer Build
- GitHub-Actions-Workflow: [smalltv-firmware-build.yml](../.github/workflows/smalltv-firmware-build.yml).
- Er checkt den auditierten Upstream-Commit `6113fb9c86e2e2024883253fd99a3d2550ffccb2` fest aus, prüft zusätzlich den erwarteten `display.cpp`-Blob, wendet beide Patches an, kopiert die lokale Decoderbibliothek und den Player hinein und baut mit `pio run -e nodemcuv2`.
- Bei Erfolg wird `firmware.bin` als 14 Tage verfügbares Actions-Artefakt abgelegt.
- Der erfolgreiche CI-Lauf bestätigt Patch-Anwendung und Kompilierung. Die Laufzeit-Allokation des Decoders im realen IRAM-Heap ist weiterhin nicht auf Hardware gemessen.

## Zweistufiger OTA-Installationsweg

- Ein eigener Minimal-Loader ist unter `firmware/loader.cpp` implementiert. Er startet das offene WLAN `SmallTV-Loader` und stellt den ESP8266-HTTP-Updater unter `/update` bereit.
- Der Loader wird als separater PlatformIO-Target gebaut und nicht in die Hauptfirmware gelinkt.
- Erfolgreicher Build mit beiden Images: [GitHub Actions Run 42805367195](https://github.com/Neferax/Ultra-TV-Fallout/actions/runs/42805367195).
- Loader: 316.112 Bytes, SHA-256 `de86b968495f03ecb0e37edeef02247202a942d7fa96dda5534564a3eef0ab2f`.
- Hauptfirmware: 701.600 Bytes, SHA-256 `9e530d102b92c251e9ed1ee36d7791077f43375d10693eff9b012619765d4df4`.
- Installationsablauf: zuerst Loader über die Stock-Seite `http://192.168.178.70/update`; danach mit `SmallTV-Loader` verbinden und die Hauptfirmware über `http://192.168.4.1/update` hochladen. Vollständige Anleitung: [INSTALLATION.md](INSTALLATION.md).
- Beide Dateien liegen gemeinsam im Actions-Artefakt `smalltv-ultra-fallout-install-package`. Der Build bestätigt die Kompilierung, nicht die Hardwarefunktion.

## Was noch offen ist
1. Decoder-Instanzgröße und IRAM-Reserve auf dem realen Gerät messen.
2. Geeignete GIFs testen: 11-Bit-LZW und vollständige Canvas-Frames; Transparenz wird schwarz dargestellt.
3. Laufzeit prüfen: Framerate, Seitenwechsel, TLS-Feed, OTA, Watchdog und Speicherfragmentierung.
4. Backup-/Restore- und Recovery-Weg für genau diese Hardware-/Partitionsvariante prüfen.

## Sicherheit und Gerätestatus
- Keine Firmware wurde geflasht.
- Keine Stock-GIFs, Einstellungen oder Dateien wurden gelöscht oder überschrieben.
- Ein erfolgreich kompiliertes Firmware-Binary liegt vor; die Hardware-Kompatibilität und der reale Laufzeitbetrieb sind noch nicht getestet.

- Konfigurationsmigration: Alte Dashboard-Konfigurationen (Schema 3) übernehmen nicht mehr die früheren Seiten-IDs; die neuen Standardseiten Uhr, Wetter und GIF-Archiv bleiben aktiv. Alte Feed-Konfigurationen (Schema 2) behalten Markt-/Home-Assistant-Einstellungen, übernehmen aber die neue Open-Meteo-Wettervoreinstellung.
- LittleFS-Uploadpfade: Temporäre Datei und Sicherung verwenden feste kurze Namen, damit gültige GIF-Dateinamen bis zur LittleFS-Komponentengrenze nicht durch angehängte Endungen unbrauchbar werden.


### Verifizierter CI-Build
- GitHub Actions: [Build-Lauf 42804144232](https://github.com/Neferax/Ultra-TV-Fallout/actions/runs/42804144232) – erfolgreich.
- PlatformIO: `pio run -e nodemcuv2` – erfolgreich.
- RAM: 47.892 von 81.920 Bytes (58,5 %).
- Flash: 697.451 von 1.044.464 Bytes (66,8 %).
- Firmware-Binary: 701.600 Bytes; SHA-256 `9e530d102b92c251e9ed1ee36d7791077f43375d10693eff9b012619765d4df4`.
- Artifact: `smalltv-ultra-fallout-esp8266`, GitHub-Aufbewahrung bis 24.11.2026.
- Noch offen: Flashen, Boot-/Displaytest, GIF-Kompatibilität, WLAN/OTA/Feed-Stabilität und Langzeittest auf dem realen Gerät.
