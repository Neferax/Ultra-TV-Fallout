# Stock-Firmware-Strategie: eigene Pip-Boy-Bildschirme

## Ergebnis der Recherche

Ein unabhängiges SmallTV-Ultra-Projekt dokumentiert die Nutzung der bereits vorhandenen HTTP-Schnittstelle der GeekMagic-Stock-Firmware. Es verändert oder ersetzt die Firmware nicht, sondern lädt 240×240-Bilder in den Bilderordner und schaltet die Anzeige auf den Photo-Album-/Bildmodus.

Dokumentierte Endpunkte aus dem untersuchten Gerät:
- `POST /doUpload?dir=/image/` – JPG/GIF in den Bilderordner hochladen.
- `GET /set?img=<path>` – ein Bild direkt anzeigen.
- `GET /set?theme=3` – Photo-Album-Modus auswählen (laut Projekt für SmallTV Ultra).
- `GET /set?i_i=<s>&autoplay=<0|1>` – Albumindex und automatische Wiedergabe steuern.
- `GET /filelist?dir=/image` – Bilddateien auflisten.
- `GET /delete?file=<path>` – Datei löschen.

Referenzprojekt: https://github.com/MacheteFlow/GeekMagic-AI-Status

## Wichtige Einschränkung

Die Referenz dokumentiert ein reales Gerät mit Firmware **Ultra-V9.0.51**. Unser Gerät meldet **Ultra-V9.0.50**. Die Endpunkte stammen aus der Stock-Firmware-Familie und sind ein vielversprechender Ansatz, aber ihre Verfügbarkeit und genaue Wirkung auf V9.0.50 müssen vor der Nutzung mit harmlosen GET-Abfragen und einem kontrollierten Test verifiziert werden.

Diese Methode verändert nicht die nativen Wetter-/Uhr-Themes. Sie zeigt stattdessen eigene fertige Grafiken über den eingebauten Bild-/Album-Modus. Das heißt:
- Eigene STAT- und DATA-Layouts sind als gerenderte 240×240-Bilder möglich.
- Die Firmware berechnet die Inhalte dieser Grafiken nicht selbst.
- Live-Daten benötigen einen Renderer, der Bilder erzeugt und bei Änderungen hochlädt. Alternativ können vorbereitete statische Grafiken manuell hochgeladen werden.
- GIFs können vom Gerät selbst abgespielt werden; Größe, Farbtiefe und Framezahl müssen wegen des knappen ESP8266-Speichers klein gehalten werden.

## Vorgeschlagener risikoarmer Ablauf

1. Nur lesende Endpunkte testen: Modell-/Versionsinfo und Dateiliste.
2. Gerätekonfiguration und vorhandene Bilddateiliste sichern.
3. Ein einzelnes Test-JPG (240×240) mit neutralem Testmotiv hochladen.
4. Dieses Bild über den Bildmodus anzeigen und anschließend auf das vorherige Theme zurückschalten.
5. Erst nach erfolgreichem Test die STAT- und DATA-Grafiken hochladen.
6. Uploads cachen: dieselbe Grafik nicht wiederholt hochladen, wenn sich ihr Inhalt nicht geändert hat.
7. GIF-Animationen erst separat testen, nachdem ein statisches Bild zuverlässig funktioniert.

## Sicherheits- und Betriebsregeln

- Keine Firmware-Updates oder alternativen Firmwareimages für diesen Ansatz.
- Keine Löschoperationen im ersten Test.
- Keine dauernden Uploads oder Sekunden-Updates: Flash-Schreibvorgänge begrenzen.
- Gerät nicht aus dem Internet erreichbar machen; die beschriebene HTTP-Schnittstelle ist unverschlüsselt und je nach Firmware ohne Authentifizierung.
- Vor Tests die vorhandenen Bilder und die aktuelle Theme-Auswahl dokumentieren.
- Test nur im lokalen WLAN durchführen.

## Designfolgen

### STAT – Hauptübersicht
Eigene 240×240-Grafik mit großer Uhr, Datum, Standort und ausgewählten Wetterwerten.

### DATA / ATMOS – Wettervorhersage
Eigenständige 240×240-Grafik mit drei Tageszeilen, Wetter-Pixelicons und Min-/Max-Temperaturen.

Die Seiten teilen die Fallout-/RobCo-Farb- und Typografiesprache, aber nicht das Layout.

## Quellen

- MacheteFlow/GeekMagic-AI-Status: https://github.com/MacheteFlow/GeekMagic-AI-Status
- GeekMagic offizielle Firmwareablage: https://github.com/GeekMagicClock/smalltv-ultra/tree/main/Ultra-V9.0.50
