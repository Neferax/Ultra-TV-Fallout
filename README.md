# Ultra-TV-Fallout

Fallout-4-/RobCo-inspiriertes Firmware-Anpassungsprojekt für die GeekMagic
SmallTV Ultra.

**Gerät:** GeekMagic SmallTV Ultra  
**Stock-Firmware:** Ultra-V9.0.50  
**Letzte bekannte Geräte-IP:** `192.168.178.70`  
**Design:** schwarzer Hintergrund, Phosphorgrün, Pip-Boy-/RobCo-Bedienelemente und gut lesbare Originaldaten.

## Geplante Displaystruktur

Die alternative Firmware erhält nur drei aktive Dashboard-Seiten:
1. Clock
2. Weather
3. GIF-Archiv

Der bisherige Status-Seitenslot wird für die GIF-Anzeige wiederverwendet. Es wird keine zusätzliche Dashboard-Seite angelegt. Uhrzeit und Wetter bleiben live über NTP und Open-Meteo.

## Tatsächlich vorhandene Arbeit

- [x] Gerät, Stock-Firmware, Speicherstand und vorhandene GIF-Dateien read-only dokumentiert
- [x] Open-Source-Firmwarebasis mit SmallTV-Ultra-Unterstützung geprüft
- [x] C++-Renderer-Patch für RobCo-Uhr und Pip-Boy-Wetter erstellt
- [x] AnimatedGIF als lokale Low-RAM-Abhängigkeit vendort
- [x] LittleFS-/TFT-Scanline-Player als Quellcode-Prototyp erstellt
- [x] GIF-Archivseite, geschützten Upload und Feed-/TLS-Speichersteuerung als Integrationspatch erstellt
- [x] GitHub-Actions-Workflow für Patch-Anwendung und PlatformIO-Build eingerichtet
- [ ] GitHub-Actions-Build erfolgreich bestätigt
- [ ] GIF-Decoder auf ESP8266-Speicherbedarf und Laufzeit geprüft
- [ ] Wetter-/Uhr-/GIF-Anzeige auf echter Hardware geprüft
- [ ] Backup-/Restore- und Recovery-Weg für die genaue Boardrevision verifiziert

## Wichtige Einschränkungen

Der GIF-Player ist auf 240×240 Pixel, maximal 300 KiB pro Datei, höchstens
11-Bit-LZW und vollständig deckende Vollbild-Frames begrenzt. Transparente oder
partielle Frames werden abgewiesen, weil kein Vollbild-Compositing-Puffer
verwendet wird. Die bestehenden Stock-GIFs wurden noch nicht auf diese
Kompatibilität geprüft.

Die Stock-GIFs werden nicht automatisch in das neue LittleFS übernommen. Sie
müssen extern gesichert und nach der Installation über die neue geschützte
Uploadseite `/gif` erneut hochgeladen werden.

## Aktueller Gerätestatus

**Am Gerät wurde nichts verändert.** Es gab keine Schreibzugriffe, Löschungen,
Theme-Wechsel oder Firmware-Updates. Es liegt noch kein nachweislich
flashfertiges Firmware-Image vor. Der Buildstatus ist nicht bestätigt.

Details: [Implementierungsstatus](docs/IMPLEMENTATION_STATUS.md) ·
[GIF-Speicher- und Decoderanalyse](docs/GIF_DECODER_FEASIBILITY.md) ·
[Offizielle Bethesda-GIF-Quellen](docs/FALLOUT_GIF_SOURCES.md) ·
[Firmware-Integration](firmware/README.md)

## Sicherheitsregeln

- Kein Flashen, bevor Build, Backup und Recovery nachgewiesen sind.
- Original-GIFs extern sichern.
- Keine unbestätigten Upload-Endpunkte automatisiert verwenden.
- Gerät nicht aus dem Internet erreichbar machen.

Fallout, Pip-Boy, RobCo und Vault-Tec sind Marken bzw. geschützte Inhalte ihrer
jeweiligen Rechteinhaber. Dieses Projekt ist ein unabhängiges Fanprojekt.
