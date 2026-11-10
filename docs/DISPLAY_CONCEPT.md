# Display-Konzept – Fallout 4 / Pip-Boy / RobCo

## Verbindliche Seitenstruktur

Die Anzeige soll genau drei Seitentypen verwenden:
1. Clock
2. Weather
3. GIF-Archiv

Die GIF-Anzeige verwendet den vorhandenen Status-Seitenslot der alternativen
Firmware. Die Gesamtzahl der Dashboard-Seiten wird nicht erhöht. Clock, Weather
und GIF sind die einzigen standardmäßig aktivierten Seiten. Die Rotation steht
standardmäßig auf 20 Sekunden.

## Gemeinsame Bildsprache

- Referenz: Fallout 4 / Pip-Boy 3000 Mark IV / RobCo
- tiefschwarzer Hintergrund
- monochromes Phosphorgrün
- kompakte technische Schrift und hohe Lesbarkeit
- RobCo-Rahmen, Statusleisten und kleine technische Kennungen
- dezente CRT-Anmutung, aber keine hektischen Vollbildblitze
- Animationen dürfen Uhr- und Wetterdaten nicht verdecken

Das Terminal-Theme ist voreingestellt. GIF-Farben werden beim Zeichnen in
monochromes Grün umgerechnet; transparente Pixel erscheinen schwarz.

## Weather

- Live-Wetter über Open-Meteo
- Standardstandort: PLZ 47239 Duisburg / Rumeln-Kaldenhausen
- aktuelle Temperatur als primärer Wert
- Wetterzustand, Höchst-/Tiefstwert und Regenwahrscheinlichkeit in kompakten
  Statusfeldern
- keine fest eingebrannten oder erfundenen Live-Werte
- Aktualisierung standardmäßig alle 30 Minuten

## Clock

- Live-NTP-Zeit und Datum
- Standardzeitzone Europe/Berlin mit automatischer CET/CEST-Umstellung
- Uhrzeit als größtes Element
- RobCo-/Vault-Tec-Kopfzeile und dezente Statusbeschriftung

## GIF-Archiv

- LittleFS-Verzeichnis `/gif/`
- geschützte Uploadseite `/gif`
- bis zu zwölf alphabetisch sortierte GIFs
- automatischer Wechsel nach 20 Sekunden
- maximal 240×240 Pixel und 300 KiB je Datei
- LZW-Codegröße höchstens 11 Bit
- Frames müssen das vollständige Canvas abdecken
- transparente Pixel werden schwarz dargestellt
- alle Bildfarben werden in Pip-Boy-Grün umgerechnet
- kein Vollbild-RGB565-Compositing-Puffer; Decoder nur während der GIF-Seite im
  sekundären IRAM-Heap

Stock-GIFs werden nicht automatisch migriert. Vor einem Firmwarewechsel müssen
Originaldateien extern gesichert und nach der Installation über `/gif`
hochgeladen werden.

## Implementierungsstatus

Die Uhr-/Wetterrenderer und die GIF-Player-/Upload-Integration liegen als
C++-Patches bzw. Quellcode-Prototyp vor. Der GitHub-Actions-Build ist eingerichtet,
aber ein erfolgreicher Build und Hardwaretest sind noch nicht bestätigt. Es gibt
noch kein nachweislich flashfertiges Image; das Gerät wurde nicht verändert.
