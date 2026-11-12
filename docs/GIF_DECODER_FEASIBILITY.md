# GIF-Wiedergabe: Machbarkeit und aktueller Implementierungsstand

## Decoder und Speicher

Verwendete Bibliothek: `bitbank2/AnimatedGIF` (Apache-2.0), lokal vendort unter
`lib/AnimatedGIF/`.

Die Firmware verwendet die vollständige 12-Bit-LZW-Konfiguration
(`MAX_CODE_SIZE=12`) und begrenzt die Bildbreite auf 240 Pixel
(`MAX_WIDTH=240`). Der Compile-Probe prüft
`sizeof(AnimatedGIF) <= 24576` Bytes.

Der Decoder wird nur während der GIF-Anzeige dynamisch mit
`new (std::nothrow)` aus dem normalen ESP8266-Heap angelegt. Vorher prüft
der Player, ob mindestens `sizeof(AnimatedGIF) + 8192` Bytes freier Heap
gemeldet werden. Bei zu wenig Speicher wird die GIF-Wiedergabe übersprungen.
Das ist eine konservative Laufzeit-Schranke, aber kein Nachweis, dass WLAN,
Webserver, TLS und Decoder unter allen Lastsituationen gleichzeitig stabil
bleiben. Ein realer Heap-Verlauf wurde auf dem Gerät noch nicht gemessen.

## Implementierter Player

Quellcode:
- `firmware/gif_player.h`
- `firmware/gif_player.cpp`
- `lib/AnimatedGIF/src/`

Der Player verwendet:
1. LittleFS-Open-/Read-/Seek-/Close-Callbacks.
2. RAW-Scanline-Ausgabe direkt über TFT_eSPI in RGB565.
3. Einen einzelnen 104-Pixel-Zeilenpuffer statt eines Vollbild-Compositing-Framebuffers.
4. Dynamische Allokation des Decoderobjekts im normalen Heap.
5. `yield()` während der Ausgabe.
6. Automatischen Wechsel zum nächsten Album-Eintrag nach 20 Sekunden.

## Bewusst unterstütztes GIF-Format

Der Player hat keinen Compositing-Framebuffer. Deshalb akzeptiert er nur:
- GIF-Canvas maximal 240 × 240 Pixel.
- Vollständige Frames, deren Ursprung bei (0,0) liegt und deren Größe exakt dem Canvas entspricht.
- Keine transparenten Frames.
- LZW-Codegröße bis zur vollständigen 12-Bit-Konfiguration.
- Dateigröße maximal 300 KiB.

Frames mit Teilbild-Offsets, abweichender Framegröße oder Transparenz werden
beim Decodieren erkannt und abgebrochen. Für den inkompatiblen Eintrag zeigt
der Player eine eigene RobCo/Pip-Boy-Fallback-Animation. Nach 20 Sekunden
versucht er den nächsten Album-Eintrag. Sind keine kompatiblen GIFs vorhanden,
bleibt die RADIO-Seite mit der Fallback-Animation nutzbar. Damit werden
Bildreste durch unvollständiges Compositing vermieden. Die GIF-Farben werden
in monochromes Pip-Boy-Phosphorgrün umgerechnet.

Die Upload-Prüfung kontrolliert Dateisignatur und Canvas-Abmessungen. Sie
validiert nicht vorab sämtliche Frame- und Transparenzeigenschaften; diese
Prüfung erfolgt während der Wiedergabe. Der Build-Workflow konvertiert das
mitgelieferte Archiv-GIF vor dem Paketieren auf 104 × 104 Pixel, opake
Vollbild-Frames und eine geordnete monochrome Grünpalette. Synthetische CI-Tests
prüfen Mehrbild-Wiedergabe, Transparenz-Flattening und den Helligkeitsverlauf. Die vorhandenen Stock-GIFs wurden
nicht gegen das unterstützte Format geprüft.

## Upload und Dateiverwaltung

Die Integration ergänzt:
- Eine RADIO/GIF-Seite.
- Upload über die geschützte Weboberfläche.
- Speicherung unter LittleFS `/gif/`.
- Bis zu zwölf alphabetisch sortierte GIF-Dateien.
- Temporäre Upload-Datei und Austausch erst nach abgeschlossenem Upload.
- Größenlimit 300 KiB pro Datei.
- Stopp/Freigabe des Decoders vor Feed-/TLS-Jobs und Netzwerkaktionen.

Ein Dateilimit von 300 KiB bedeutet nicht, dass jede Datei auf dem Gerät
hochgeladen werden kann: verfügbarer LittleFS-Speicher und Reserve für
Dateisystem-Metadaten begrenzen die tatsächlich mögliche Größe zusätzlich.

## Build- und Teststatus

Der GitHub-Actions-Workflow
`.github/workflows/smalltv-firmware-build.yml` kompiliert für PlatformIO
`nodemcuv2`, prüft die Decoder-Instanzgröße und erzeugt native
240×240-Renderer-Vorschauen.

Ein erfolgreicher CI-Build bestätigt die Kompilierung und die statischen
Build-Prüfungen. Er bestätigt nicht die tatsächliche GIF-Framerate,
Laufzeit-Heap-Reserve, Watchdog-Stabilität, TLS-Wechsel oder die Wiedergabe
auf dem realen SmallTV.

**Hardwaretest weiterhin offen.** Es wurde nichts auf das Gerät geflasht
oder verändert.

## Voraussetzungen vor einem Flash

Vor einem Flash müssen mindestens geprüft werden:
- Build und Decoder-Compile-Probe erfolgreich.
- Geeignete GIF-Dateien mit vollständigen, opaken Canvas-Frames.
- Backup der vorhandenen LittleFS-Dateien.
- Ausreichender Heap während GIF-Wiedergabe und nachfolgendem Feed-/TLS-Job.
- Kein Watchdog-Reset und kein sichtbarer Bildfehler bei längerer Wiedergabe.
- Wiederherstellung der normalen Anzeige nach Verlassen von RADIO.
