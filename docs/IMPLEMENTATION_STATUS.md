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
2. GIF-Wiedergabe und den vorhandenen Album-Ablauf implementieren. Die aktuelle Upstream-Quelle enthält keinen GIF-Player. Die Upstream-Historie dokumentiert die bewusste Entfernung der JPEG-Bildfunktion und ihrer Decoder-Abhängigkeit. Der Standarddecoder AnimatedGIF benötigt laut Beispiel rund 22,5 KB RAM; die dokumentierte freie DRAM-Reserve des Upstream-Geräts liegt nach normalem Start bei etwa 18,5 KB. Eine unveränderte Integration ist daher nicht vertretbar. Siehe [GIF-Decoder-Machbarkeit](GIF_DECODER_FEASIBILITY.md).
3. Prüfen, wie Wetter-/WLAN-Konfiguration aus dem bisherigen Gerät übernommen werden kann.
4. Exakte Boardrevision, Flash-Layout und Recovery-Weg vor jeder Geräteinstallation verifizieren.


## Reproduzierbarer Build-Check
- GitHub Actions Workflow ergänzt: [smalltv-firmware-build.yml](../.github/workflows/smalltv-firmware-build.yml).
- Der Workflow checkt den SmallTV-Upstream aus, prüft den exakten `src/display.cpp`-Ausgangsblob, wendet den Renderer-Patch mit `git apply --check` an und baut anschließend `pio run -e nodemcuv2`.
- Bei erfolgreichem Lauf wird `firmware.bin` als 14 Tage verfügbares Actions-Artefakt abgelegt.
- Commit mit Workflow: `086332b96f6e5bec1de9215d918e87fdd4794572`.
- **Laufstatus noch nicht bestätigt:** Die verfügbaren GitHub-Abfragen liefern für diesen Commit bislang keine Status-Checks. Daher wird der Build nicht als erfolgreich bezeichnet.
- Der Workflow baut derzeit nur den Uhr-/Wetter-Renderer-Patch. Er enthält noch keine GIF-Integration und erzeugt noch kein vollständiges Fallout-System mit GIF-Karussell.

## Neue Erkenntnisse zur GIF-Integration (10.11.2026)
- Hauptloop geprüft: `feedsLoop()` und `displayUpdate()` laufen unabhängig; ein GIF-Player muss Feed-/TLS-Jobs ausdrücklich priorisieren.
- Feed-Code nutzt `HeapSelectIram` für BearSSL-Puffer und prüft freie DRAM-/Gesamtheap-Reserven. Eine GIF-Instanz darf deshalb nicht parallel zu TLS im Sekundärheap verbleiben.
- AnimatedGIF legt die großen LZW-/Pixelpuffer direkt in der Decoder-Instanz ab. Ein `MAX_CODE_SIZE=10`-Prototyp hat rund 8,7 KB große Array-Puffer (ohne Struktur-Overhead); das ist eine Header-basierte Abschätzung, keine gemessene Instanzgröße.
- Die Decoder-Integration wird erst nach Messung von `sizeof(AnimatedGIF)`, IRAM-`largestBlock`, LittleFS-Callback-Funktion und erfolgreichem isoliertem Build begonnen.
- Detail: [GIF-Decoder-Machbarkeit](GIF_DECODER_FEASIBILITY.md), aktualisiert am Commit `bcbfc05d85c622a65eb672d99eb315b761a0fb57`.

## Was ausdrücklich NICHT fertig ist
- Kein vollständiger Fallout-Firmwarebuild.
- Keine Änderung am Gerät.
- Keine GIF-Datei am Gerät ersetzt oder gelöscht.
- Kein flashfertiges Installationspaket.
- Keine bestätigte GIF-Karussell-Wiedergabe in der alternativen Firmware.
- Keine GIF-Decoder-Integration; Speicherbudget und notwendige Einschränkungen sind dokumentiert.

## Sicherheit
- Kein Flashen, Löschen oder Überschreiben.
- Original-GIFs bleiben unangetastet.
- Keine unbestätigten Upload-Endpunkte automatisiert verwenden.
- Keine Behauptung eines erfolgreichen Builds ohne tatsächlichen Compile- und Validierungslauf.
