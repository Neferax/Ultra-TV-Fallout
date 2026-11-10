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


## Konkreter Speicheransatz für den nächsten Prototyp

Ein möglicher Weg ist, den Decoder nicht dauerhaft im primären DRAM zu halten:
- `MAX_CODE_SIZE=11` würde die großen LZW-Tabellen-/Pixelpuffer gegenüber dem Standardwert 12 deutlich verkleinern.
- Die GIF-Dateien müssten vorab kontrolliert neu encodiert werden; beliebige GIFs wären nicht mehr garantiert kompatibel.
- Die Decoder-Instanz könnte testweise nur während der GIF-Seite dynamisch im sekundären IRAM-Heap angelegt werden.
- Vor jedem Feed-/TLS-Job müsste die Wiedergabe beendet und die Instanz freigegeben sein, da BearSSL denselben sekundären Heap für seine Puffer nutzt.

[Schlussfolgerung] Mit dem in der Hardwaremessung protokollierten IRAM-Freiraum von rund 18.8 KB könnte eine reduzierte Decoder-Instanz grundsätzlich in Frage kommen. Das ist noch kein Nachweis: `sizeof(AnimatedGIF)`, tatsächliche IRAM-Allokation, größter freier Block und Verhalten beim Wechsel zwischen GIF und TLS müssen auf dem echten Build gemessen werden. Bei zu wenig IRAM wird die GIF-Seite deaktiviert statt den Netzwerkbetrieb zu riskieren.

## Zusätzliche Prüfung: tatsächlicher Hauptloop und Heap-Auswahl

Die aktuelle Upstream-Implementierung wurde zusätzlich direkt in den relevanten
Quellstellen geprüft:

- `src/main.cpp`: `feedsLoop()` wird im Hauptloop aufgerufen; danach kann
  `displayUpdate()` weiterhin laufen. Ein GIF-Player darf daher nicht einfach
  im Renderpfad Speicher belegen, während ein Feed-Worker aktiv ist.
- `src/feeds.cpp`: BearSSL verwendet explizit `HeapSelectIram` für TLS-Puffer.
  Die HTTPS-Freigabe prüft mindestens 20 KB freien DRAM-Heap und einen
  kombinierten freien Heap von 38 KB; zusätzlich muss ein ausreichend großer
  zusammenhängender Block für den TLS-Empfangspuffer verfügbar sein.
- `src/display.cpp`: Es existiert bereits `displaySuspendDynamicResources()`
  für die dynamischen Clock-Sprite-Ressourcen. Das ist ein vorhandener
  Integrationsmechanismus, ersetzt aber keine GIF-spezifische Speicherverwaltung.
- `src/dashboard.h`: Die Seitenrotation ist auf die vorhandenen Dashboard-IDs
  ausgelegt. Ein GIF-Karussell ist keine bereits vorhandene Seite und muss
  ausdrücklich in Seitenverfügbarkeit, Rotation und Rendering integriert werden.

### Konsequenz für den Decoder-Prototyp

Der Header von AnimatedGIF legt die großen Decoder-Puffer direkt in
`GIFIMAGE` ab, das wiederum Bestandteil der `AnimatedGIF`-Instanz ist.
Bei `MAX_CODE_SIZE=11` ergeben allein die großen Arrays näherungsweise:

| Puffer | Größe |
|---|---:|
| Datei-/LZW-Pixelstack | 1.024 B |
| globale + lokale Palette | 1.536 B |
| LZW-Chunkpuffer | 1.530 B |
| Turbo-LZW-Tabelle | 2.048 B |
| Turbo-Pixelpuffer | 2.048 B |
| Zeilenpuffer | 495 B |
| **Summe der Arrays** | **8.681 B** |

Hinzu kommen Strukturfelder und Zeiger. Das ist eine Größenabschätzung aus den
Header-Arrays, kein gemessener `sizeof(AnimatedGIF)`-Wert. Die Turbo-Puffer
werden in RAW-Scanline-Wiedergabe nicht als zusätzlicher Framebuffer angefordert,
liegen aber als feste Arrays trotzdem in der Instanz.

### Erforderliche Ablaufsteuerung

1. Vor dem Start eines Feed-/TLS-Jobs GIF-Datei schließen, Decoder-Instanz
   freigeben und IRAM-Heap-Auswahl sauber zurücksetzen.
2. GIF-Player nur starten, wenn kein Feed-Job und keine Netzwerkaktion läuft.
3. Während eines GIF-Frames regelmäßig `yield()` ausführen und die
   Frame-Wartezeit nicht blockierend über `millis()` verwalten.
4. Feed-Jobs erhalten Vorrang; nach Ende des Jobs darf der GIF-Player auf der
   aktuellen Albumposition wieder starten.
5. Bei fehlender IRAM-Blockgröße oder Allokationsfehler die GIF-Seite überspringen,
   nicht in den DRAM-Fallback wechseln.

**Wichtige offene Messung:** Die Upstream-Hardware-Auditwerte nennen rund
18.8 KB freien IRAM-Heap nach dem Start. Das ist ein historischer Messwert und
kein garantierter Wert für jeden Bootzustand. Vor einem echten Player müssen
`sizeof(AnimatedGIF)`, IRAM-Heap-`free` und `largestBlock` im konkreten Build
protokolliert werden. Der Decoder-Fork muss außerdem tatsächlich mit
`MAX_CODE_SIZE=11` gebaut werden; das einfache Überschreiben des Makros vor
einem unveränderten Bibliotheksheader reicht nicht.

**Entscheidung:** Noch keine GIF-Player-Integration in `main.cpp` oder
`display.cpp`. Zuerst ist ein isolierter Decoder-Prototyp mit gemessener
IRAM-Allokation und LittleFS-Callbacks nötig. Erst danach wird die zusätzliche
Dashboard-Seite angelegt. So bleibt die funktionierende Uhr-/Wetter-/TLS-Basis
unangetastet.
