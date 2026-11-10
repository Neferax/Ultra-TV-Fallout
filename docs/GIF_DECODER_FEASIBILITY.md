# GIF-Wiedergabe: Machbarkeit und aktueller Implementierungsstand

## Ausgangslage

Die aktuelle Quelle von `iodn/geekmagic-tv-esp8266` enthält keine GIF-Wiedergabe.
Die Projekt-Historie dokumentiert die Entfernung der früheren JPEG-/Bildfunktion
und ihrer Decoder-Abhängigkeit. Ein GIF-Player muss deshalb neu integriert werden.

## Decoder und Speicher

Verwendete Bibliothek: `bitbank2/AnimatedGIF` (Apache-2.0), lokal vendort unter
`lib/AnimatedGIF/`.

Die Standardkonfiguration reserviert laut Bibliotheksbeispiel rund 22,5 KB RAM.
Die historische Hardwaremessung des Upstream-Projekts meldet nach normalem Start
rund 18,5 KB freien DRAM und 18,8 KB freien sekundären IRAM-Heap. Ein
Standarddecoder passt daher nicht einfach in den freien DRAM.

Für den ESP8266 wurde die Bibliothek gezielt reduziert:
- `MAX_CODE_SIZE=11`: LZW-Codes bis 11 Bit.
- `MAX_WIDTH=240`: Bildbreite passend zum Display.
- Die Instanz wird nur während der GIF-Anzeige im sekundären Heap angelegt.
- Der Build-Probe erzwingt `sizeof(AnimatedGIF) <= 15360` Bytes.
- Vor der Allokation prüft der Player den größten freien IRAM-Block und lässt
  mindestens 2 KB Reserve. Bei zu wenig Speicher wird die GIF-Wiedergabe
  übersprungen; es gibt keinen DRAM-Fallback.

Die großen festen Arrays der 11-Bit-Konfiguration benötigen näherungsweise:

| Puffer | Größe |
|---|---:|
| Datei-/LZW-Pixelstack | 2.048 B |
| globale + lokale Palette | 1.536 B |
| LZW-Chunkpuffer | 1.530 B |
| Turbo-LZW-Tabelle | 4.096 B |
| Turbo-Pixelpuffer | 4.096 B |
| Zeilenpuffer (240 + 15) | 255 B |
| **Summe der Arrays** | **13.561 B** |

Das ist eine Berechnung aus den Array-Dimensionen des Headers, kein gemessener
`sizeof(AnimatedGIF)`-Wert. Der Compile-Probe prüft die Obergrenze beim Build.

## Implementierter Prototyp

Quellcode:
- `firmware/gif_player.h`
- `firmware/gif_player.cpp`
- `lib/AnimatedGIF/src/`

Der Player verwendet:
1. LittleFS-Open-/Read-/Seek-/Close-Callbacks.
2. RAW-Scanline-Ausgabe direkt über TFT_eSPI in RGB565.
3. Einen einzelnen 240-Pixel-Zeilenpuffer statt eines Vollbild-Framebuffers.
4. Dynamische Allokation des Decoderobjekts im IRAM-Heap.
5. `yield()` nach jeder ausgegebenen Zeile.

### Bewusste GIF-Einschränkungen

Ohne Compositing-Framebuffer kann der Player keine beliebigen GIF-Frames korrekt
zusammensetzen. Er akzeptiert daher nur:
- Canvas maximal 240 × 240 Pixel.
- Vollständige, deckende Frames, die jeweils das ganze GIF-Canvas abdecken.
- Transparente Pixel werden beim Zeichnen zu Schwarz abgeflacht.
- Keine Disposal-Methode 2.
- LZW-Codegröße maximal 11 Bit.
- Dateigröße maximal 300 KiB.

Partielle Frames und Disposal-Methode 2 werden abgewiesen. Transparenz wird
auf schwarzem Hintergrund abgeflacht. Alle sichtbaren GIF-Farben werden in
monochromes Pip-Boy-Phosphorgrün umgerechnet. Die Dateien müssen entsprechend vorbereitet
sein. Die vorhandenen Stock-GIFs wurden noch nicht gegen diese Anforderungen
geprüft.

## Integration in die Firmware

`patches/0002-gif-player-integration.patch` ergänzt:
- Eine GIF-Seite direkt nach Weather in der Seitenrotation.
- Eine geschützte Upload-Seite unter `/gif`.
- Speicherung unter LittleFS `/gif/`.
- Bis zu zwölf alphabetisch sortierte GIF-Dateien.
- Temporäre Upload-Datei und Austausch erst nach vollständigem Upload.
- Automatischen Wechsel zum nächsten GIF nach 20 Sekunden.
- Stoppen und Freigeben des Decoders vor Feed-/TLS-Jobs, OTA und anstehenden
  Netzwerkaktionen.

Die Originaldateien aus der Stock-Firmware werden nicht automatisch in das neue
LittleFS übernommen. Sie müssen extern gesichert und nach Installation über
`/gif` erneut hochgeladen werden.

## Build- und Teststatus

Ein GitHub-Actions-Workflow ist eingerichtet:
`.github/workflows/smalltv-firmware-build.yml`. Er:
- prüft den erwarteten Upstream-Quellstand,
- wendet den Fallout-Uhr-/Wetter-Patch an,
- kopiert die lokale Decoderbibliothek und den Player,
- wendet die GIF-Integrationspatches an,
- kompiliert mit PlatformIO für `nodemcuv2`,
- legt bei Erfolg das Firmware-Binary als Artefakt ab.

**Der Buildstatus konnte über die verfügbaren GitHub-Abfragen nicht bestätigt
werden.** Daher sind Compile-Erfolg, tatsächliche Instanzgröße, IRAM-Allokation,
GIF-Framerate, Watchdog-Stabilität und TLS-Wechsel weiterhin nicht verifiziert.
Es wurde nichts auf das SmallTV-Gerät geflasht oder verändert.

## Abbruchkriterien

Die GIF-Seite bleibt deaktiviert bzw. wird übersprungen, wenn:
- der Compile-Probe die 15-KB-Instanzgrenze überschreitet,
- der größte freie IRAM-Block nicht ausreicht,
- die TLS-Reserve nach dem Freigeben nicht wiederhergestellt wird,
- Laufzeitfehler oder Watchdog-Resets auftreten.

Kein Flashen, bevor Build, Laufzeit, Backup/Restore und Recovery für die genaue
Hardwarevariante nachgewiesen sind.
