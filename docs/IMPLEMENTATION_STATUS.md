# Implementierungsstatus – 10.11.2026

## Gerät
- GeekMagic SmallTV Ultra, Firmware Ultra-V9.0.50
- IP: `192.168.178.70`
- Aktuelles Theme laut letzter Auslesung: 7
- Freier Speicher zuletzt gemeldet: 187.916 Bytes (ca. 183,5 KiB)

## Verbindliches Ziel
Eine Wetterseite, eine Uhrseite und die vorhandenen GIF-Anzeigen dazwischen. Alle Bestandteile sollen ein zusammenhängendes Fallout-4-/Pip-Boy-3000-Mark-IV-Design erhalten. Wetter, Uhrzeit, Datum, WLAN und der bisherige Ablauf sollen erhalten bleiben. Keine unnötigen zusätzlichen Seiten.

## Tatsächlich erledigt
- Gerät, Firmwareversion, relevante Speicherwerte und vorhandene GIF-Dateien dokumentiert.
- Stock-Firmware-Endpunkte read-only untersucht; keine Schreiboperation am Gerät ausgeführt.
- Kompatibilitätsprüfung von `smalltv-mod`: dessen Theme-Engine skinnt nicht die Stock-Wetterseite, Stock-Uhrseite und GIF-Rotation.
- Bessere Open-Source-Basis identifiziert: [iodn/geekmagic-tv-esp8266](https://github.com/iodn/geekmagic-tv-esp8266). Das Projekt nennt SmallTV Ultra ausdrücklich als getestete ESP8266-Hardware und enthält getrennte C++-Renderer für Uhr und Wetter.
- Ersten konkreten C++-Quellcode-Patch erstellt: [patches/0001-fallout-pipboy-renderers.patch](../patches/0001-fallout-pipboy-renderers.patch). Er ersetzt die generischen Uhr-/Wetterlayouts durch RobCo-/Pip-Boy-Panels und behält die vorhandenen NTP- und Open-Meteo-Datenpfade bei.
- Integrationshinweise und Einschränkungen dokumentiert: [firmware/README.md](../firmware/README.md).

## Aktueller Stand des Quellcode-Patches
- Patch basiert auf dem upstream `src/display.cpp` Blob `ef482ea3cc556eb414fff6178fcc7a4d136563a9`.
- Patch wurde in diesem Repository abgelegt, aber noch nicht gegen einen lokalen vollständigen Upstream-Checkout mit `git apply` validiert.
- Nicht kompiliert, nicht auf Hardware getestet und ausdrücklich kein flashfertiges Image.
- Als Ausgangsfarbschema ist das eingebaute Terminal-Theme (ID 2) vorgesehen; benutzerdefinierte Schwarz-/Grünwerte sind in `firmware/README.md` dokumentiert.

## Offene Kernarbeit
1. Patch in einem vollständigen Upstream-Checkout anwenden und kompilieren; Compilerfehler korrigieren.
2. GIF-Wiedergabe und den vorhandenen Album-Ablauf implementieren. In den durchsuchten Upstream-Quellen wurde kein GIF-Decoder bzw. keine AnimatedGIF-Integration gefunden. Die dokumentierte Bildfunktion betrifft temporäre JPEGs; außerdem wird `/image/` beim Start geleert.
3. Prüfen, wie Wetter-/WLAN-Konfiguration aus dem bisherigen Gerät übernommen werden kann.
4. Exakte Boardrevision, Flash-Layout und Recovery-Weg vor jeder Geräteinstallation verifizieren.

## Was ausdrücklich NICHT fertig ist
- Kein vollständiger Fallout-Firmwarebuild.
- Keine Änderung am Gerät.
- Keine GIF-Datei am Gerät ersetzt oder gelöscht.
- Kein flashfertiges Installationspaket.
- Keine bestätigte GIF-Karussell-Wiedergabe in der alternativen Firmware.

## Sicherheit
- Kein Flashen, Löschen oder Überschreiben.
- Original-GIFs bleiben unangetastet.
- Keine unbestätigten Upload-Endpunkte automatisiert verwenden.
- Keine Behauptung eines erfolgreichen Builds ohne tatsächlichen Compile- und Validierungslauf.
