# Stock-Firmware API – Bildspeicher und Photo Album

## Gerätebefund

Am Gerät des Projekts wurde am 10.11.2026 geprüft:

- IP im lokalen Netz: `192.168.178.70`
- `GET /v.json` liefert `{"m":"SmallTV-Ultra","v":"Ultra-V9.0.50"}`
- `GET /filelist?dir=/image` liefert eine HTML-Dateiliste mit sieben GIF-Dateien:

| Datei | Größe |
|---|---:|
| `1000042071.gif` | 282 KB |
| `1000042073.gif` | 6 KB |
| `1000042075.gif` | 28 KB |
| `1000042077.gif` | 120 KB |
| `1000042080.gif` | 94 KB |
| `1000042085.gif` | 112 KB |
| `1000042086.gif` | 175 KB |

Die Dateiliste bestätigt, dass das Gerät den Bildordner lesen und seine Inhalte über das Webinterface auflisten kann. Sie beweist noch nicht, welches GIF aktuell angezeigt wird oder ob die Dateien ohne Einschränkung abspielbar sind.

## In Community-Projekten dokumentierte Stock-API

Mehrere unabhängige Community-Referenzen beschreiben für die SmallTV-Ultra-Stock-Firmware folgende Abläufe:

- Bild/GIF hochladen: `POST /doUpload?dir=/image/`
- Einzelbild auswählen: `GET /set?img=/image/<filename>`
- Photo-Album-Modus auswählen: `GET /set?theme=3`
- Speicherstatus lesen: `GET /space.json`
- Gerätestatus lesen: `GET /app.json`
- Bilddateien auflisten: `GET /filelist?dir=/image/`

Quellen:
- https://github.com/adrienbrault/geekmagic-hacs
- https://github.com/epicsagas/AgentGlance
- https://github.com/lucasfogacadj/smalltv-mascot

**Wichtige Einschränkung:** Diese Endpunkte sind Community-dokumentiert. Auf dem konkreten Gerät wurden bisher nur `/v.json` und `/filelist?dir=/image` tatsächlich aufgerufen. Die Schreiboperationen `/set`, Upload und Delete wurden noch nicht getestet.

## Nächste sichere Prüfschritte

Nur lesende Abfragen:

1. `http://192.168.178.70/space.json` – Gesamt- und freier Speicher.
2. `http://192.168.178.70/app.json` – aktueller App-/Theme-Zustand, sofern in dieser Version verfügbar.

Keine Lösch-, Upload-, Theme- oder Bild-Setzoperation ausführen, bevor der Nutzer den konkreten Test ausdrücklich freigibt.

## Konsequenz für das Projekt

Die vorhandene Photo-Album-Funktion könnte als Darstellungsebene für eigene 240×240-Pixel-Fallout/Pip-Boy-Bildschirme dienen. Damit wäre zunächst keine Änderung der Firmware-Binärdatei erforderlich. Ob sich mehrere Ansichten automatisiert wechseln lassen und wie die originale Wetter-/Uhrseiten-Navigation dabei erhalten bleibt, ist noch offen.

Animationen sparsam dimensionieren: Das Hersteller-Changelog weist in einer älteren Version auf mögliche Neustarts bei Theme-Loops durch knappen RAM hin. Die vorhandenen Dateigrößen sind keine Aussage über den RAM-Bedarf beim GIF-Decoding.
