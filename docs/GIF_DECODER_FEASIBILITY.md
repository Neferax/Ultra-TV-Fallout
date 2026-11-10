# GIF-Wiedergabe: Machbarkeit und Speicherbudget

## Ergebnis der Quellcodeprüfung

Die aktuelle Quelle von `iodn/geekmagic-tv-esp8266` enthält keine GIF-Wiedergabe.
Die Projekt-Historie dokumentiert am 14.10.2026 ausdrücklich, dass JPEG-Rendering,
Bild-Uploads, Bildrouten, Dashboard-Bedienelemente und die Decoder-Abhängigkeit
entfernt wurden. Der aktuelle README-Text des Upstream-Projekts enthält an dieser
Stelle noch ältere Angaben und ist nicht mit dem aktuellen Quellcode synchron.

Quelle: `audit/sync-all-and-clock-verification.txt` im Upstream-Projekt.

## Kandidat: bitbank2/AnimatedGIF

Die Bibliothek trennt Dateizugriff, Dekodierung und Display-Ausgabe über Callbacks.
Für den SmallTV wäre die passende Architektur:

1. GIF-Datei aus LittleFS streamen (Open/Read/Seek/Close-Callbacks).
2. Jede dekodierte Scanline direkt an TFT_eSPI übertragen.
3. Keinen 240x240 RGB565-Framebuffer anlegen.
4. GIF nur während der Bildphase abspielen; Feed-/TLS-Arbeit hat Vorrang.
5. Bei Ende oder Fehler Datei schließen und zur nächsten Album-Datei wechseln.

Die öffentliche API unterstützt dateibasierte `open(...)`-Callbacks und
`playFrame(...)`. Der Decoder-Callback erhält Zeilenpixel und Palette.
Quelle: [AnimatedGIF API](https://github.com/bitbank2/AnimatedGIF/wiki).

## Kritischer RAM-Befund

Das AnimatedGIF-Beispiel nennt für die Instanz rund **22,5 KB RAM**. Der Header
enthält unter anderem einen LZW-Tabellenpuffer mit 4096 Einträgen, einen
Pixelpuffer und einen Zeilenpuffer. Die Bibliothek erlaubt, `MAX_CODE_SIZE`
herabzusetzen, wenn sämtliche GIFs gezielt dafür encodiert werden. Das ist keine
universelle Kompatibilität mehr: GIFs, die größere LZW-Codes benötigen, können
damit nicht zuverlässig dekodiert werden.

Quellen:
- [AnimatedGIF TFT_eSPI example](https://github.com/bitbank2/AnimatedGIF/blob/master/examples/TFT_eSPI_memory/TFT_eSPI_memory.ino)
- [AnimatedGIF header](https://github.com/bitbank2/AnimatedGIF/blob/master/src/AnimatedGIF.h)

Die Upstream-Hardwaremessung vom 14.10.2026 meldet nach normalem Start ungefähr
18.5 KB freie DRAM. Damit passt eine normale 22.5-KB-Decoderinstanz nicht einfach
in den vorhandenen freien DRAM. TLS benötigt zusätzlich freie DRAM-Blöcke und
Sekundärheap-Puffer. Ein global hinzugefügter Standarddecoder wäre deshalb kein
vertretbarer erster Versuch.

## Nächster Implementierungsschritt

- Kleinen Decoder-Fork mit reduzierter `MAX_CODE_SIZE`-Konfiguration untersuchen.
- Instanz- und Heap-Größen mit dem ESP8266-Compiler messen, nicht schätzen.
- GIFs vorab in ein kontrolliertes Format umcodieren; Originaldateien separat sichern.
- Erst einen GIF-Testplayer ohne Netzwerkzugriffe kompilieren.
- Danach den Player in den Seitenwechsel integrieren und während Feed-/TLS-Jobs pausieren.
- Laufzeitmessung: DRAM frei/größter Block, IRAM frei, Framerate, Watchdog und Bootstabilität.

## Abbruchkriterien

Kein Einbau in den Hauptloop, wenn der Player die TLS-Reserve unterschreitet,
den größten freien DRAM-Block zu stark fragmentiert oder den Watchdog auslöst.
Kein Flashen auf das Nutzergerät, bevor Backup/Restore der Original-GIFs und
Recovery für die genaue Hardwarevariante nachgewiesen sind.

**Status:** Analyse abgeschlossen, Decoder noch nicht integriert, nicht kompiliert
und nicht auf Hardware getestet.
