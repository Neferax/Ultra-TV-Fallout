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


## GIF-Seite und Upload-Integration (Patch erstellt)
- `patches/0002-gif-player-integration.patch` ergänzt die Dashboard-Seite **direkt nach Weather**, die Konfigurationsversion und die Seitenrotation.
- Der Webserver erhält `/gif` als geschützte Upload-Seite und `POST /gif/upload`; Dateien landen in `/gif/` in LittleFS. Uploads schreiben zunächst in eine temporäre Datei und ersetzen erst nach erfolgreichem Abschluss.
- Die GIF-Seite spielt bis zu zwölf alphabetisch sortierte Dateien ab und wechselt nach 20 Sekunden zur nächsten Datei.
- Feed-/TLS-Arbeit, OTA und anstehende Netzwerkaktionen stoppen den Decoder und geben seinen IRAM-Speicher frei.
- Das Gerät bekommt damit keine automatische Übernahme seiner alten Stock-GIFs. Die alten Dateien müssen extern gesichert und nach der Installation über `/gif` erneut hochgeladen werden.
- Einschränkungen: maximal 300 KiB pro GIF, 240 px Canvas-Breite, LZW-Codegröße höchstens 10 Bit, nur vollständig deckende Vollbild-Frames. Transparente oder partielle Frames werden abgewiesen, da kein voller Compositing-Framebuffer reserviert wird.
- Der CI-Workflow wendet jetzt beide Patches an und kompiliert den Player samt Bibliothek. Der verfügbare Status-Endpunkt meldet noch keine Checks; Build und Laufzeit sind daher weiterhin **unbestätigt**.

## GIF-Player-Prototyp (Quellcode vorhanden)
- `firmware/gif_player.h/.cpp` enthält jetzt einen isolierten Player: LittleFS-Datei-Callbacks, AnimatedGIF-RAW-Scanlines, RGB565-Ausgabe über TFT_eSPI und zentrierte Darstellung auf 240×240.
- Decoder-Instanz wird nur bei Start im `HeapSelectIram` angelegt; vor dem Freigeben wird die Datei geschlossen und das Objekt wieder im selben Heap freigegeben.
- Die LittleFS-Callbacks aktualisieren explizit `GIFFILE.iPos`; das ist für die Positionslogik des Decoders erforderlich.
- Vor Start wird `largestBlock` und `free` des IRAM-Heaps gegen `sizeof(AnimatedGIF)+2048` geprüft. Bei zu wenig Speicher wird nicht auf DRAM ausgewichen.
- Der Player akzeptiert derzeit nur vorab abgeflachte, vollständig deckende Frames ohne Transparenz und ohne Disposal-Methode 2. Partielle Frames würden ohne Compositing-Puffer Bildreste erzeugen und werden deshalb abgewiesen.
- Der Player ist noch **nicht** mit Hauptloop, Feed-Worker, Upload-Endpunkt, Album-Dateiliste oder Dashboard-Seitenrotation verbunden. Der Aufrufer muss ihn vor jedem Netzwerk-/TLS-Job stoppen.
- Der CI-Workflow kopiert nun Player, Header und Low-RAM-Bibliothek in den Upstream-Checkout und versucht den ESP8266-Build. Ein erfolgreicher Lauf ist über die verfügbaren Statusabfragen noch nicht bestätigt.

## GIF-Decoder: erster echter Build-Baustein
- AnimatedGIF wurde mit Apache-2.0-Lizenz lokal in `lib/AnimatedGIF/` vendort.
- Die lokale Kopie begrenzt `MAX_CODE_SIZE` auf 10 und `MAX_WIDTH` auf 240. Die Bibliothek ist damit nur für eigens passend encodierte GIF-Dateien vorgesehen; beliebige GIFs sind nicht garantiert kompatibel.
- `firmware/gif_decoder_probe.cpp` erzwingt beim Build die beiden Konfigurationswerte und macht die tatsächliche Instanzgröße über `sizeof(AnimatedGIF)` messbar.
- Der GitHub-Actions-Workflow kopiert Bibliothek und Probe in den Upstream-Checkout und kompiliert sie zusammen mit dem vorhandenen Firmwareprojekt.
- Noch nicht vorhanden: LittleFS-Datei-Callbacks, Scanline-Ausgabe, Albumverwaltung, Feed-Priorisierung und Dashboard-Seitenintegration.
- CI-Status weiterhin nicht bestätigt; keine Behauptung eines erfolgreichen Builds.

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
