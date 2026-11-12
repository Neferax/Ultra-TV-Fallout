# Ultra-TV-Fallout

Fallout-4-/Pip-Boy-Oberfläche für die GeekMagic SmallTV Ultra (ESP8266, ST7789, 240x240).

> **Status: Build 298 erfolgreich, native Vorschauen visuell geprüft.** Die aktuelle Wetteransicht zeigt Temperatur, Wetterlage sowie gefühlte Temperatur, Luftfeuchte, Wind, Böen, Niederschlag, Regenwahrscheinlichkeit, UV und Sonnenzeiten. Die separate Drei-Tage-Vorschau ist auf zwei große Zeilen pro Tag reduziert. STAT und RADIO bleiben eigenständige Seiten. Eine Prüfung auf dem echten Gerät steht noch aus; Build 298 ist daher noch keine Hardwarefreigabe.

## Verbindliche Zielstruktur

Drei vorhandene Seiten-Slots, keine zusätzlichen Dashboard-Seiten:

1. **STAT** – Uhrzeit und Datum, klarer Hauptfokus.
2. **DATA** – Wetter mit Temperatur, Zustand, Luftfeuchte, Regen, Wind und kurzer Vorhersage.
3. **RADIO** – eigenständiges Animations-/Vault-Tec-Archivfenster.

Designreferenz ist der Pip-Boy 3000 Mark IV aus Fallout 4: monochrom, text- und zahlenorientiert, klare Registerleiste, dünne Trennlinien, wenige gezielte Grafiken. Keine beliebigen Neon-/Cyberpunk-Effekte oder übereinanderliegenden Inhalte.

## Recherche und Designunterlagen

- [Vergleich vorhandener SmallTV-Projekte](docs/DESIGN_REFERENCE_COMPARISON.md)
- [Verbindlicher neuer Displayentwurf und Abnahmekriterien](docs/DISPLAY_CONCEPT.md)
- [Implementierungsstatus](docs/IMPLEMENTATION_STATUS.md)

Verglichene Projekte:
- [iodn/geekmagic-tv-esp8266](https://github.com/iodn/geekmagic-tv-esp8266) – getestete SmallTV-Ultra-Basis mit nativen Display-Renderer-Vorschauen.
- [giovi321/smalltv-mod](https://github.com/giovi321/smalltv-mod) / [SmallTV Studio](https://giovi321.github.io/smalltv-studio/) – visueller 240x240-Theme-Editor und fertige Layoutbeispiele.
- [u1pns/smalltv-ultra](https://github.com/u1pns/smalltv-ultra) – Browser-seitige Bild-/GIF-Vorverarbeitung statt Laufzeit-Decodierung auf dem ESP8266.
- [msdxlab/SmallTV-ultra-mod](https://github.com/msdxlab/SmallTV-ultra-mod) – Referenz für Teilaktualisierung und Screen-Mirror.

Diese Projekte liefern Layout-, Test- und Technikreferenzen. Ihre Firmware-Images und Theme-Pakete sind nicht ohne Prüfung austauschbar.

## Qualitätsregeln

- Vorschauen müssen exakt 240x240 Pixel groß sein und dieselben Bitmap-Fonts wie die Firmware nutzen.
- Lange deutsche Wochentage, fehlende Wetterdaten, lange Werte und Seitenwechsel werden geprüft.
- Keine abgeschnittenen oder überlagerten Inhalte; Seitenwechsel dürfen keine alten Pixel hinterlassen.
- Wetterwerte müssen aus echten Daten stammen; fehlende Werte werden als -- oder NO SIGNAL angezeigt.
- GIFs werden bevorzugt vor dem Upload in kleine, begrenzte Sprites umgewandelt.
- Ein erfolgreicher CI-Build allein ist keine Design- oder Hardwarefreigabe.

## Technischer Stand

- Repository-Quellcode und GitHub-Actions-Build existieren.
- Build 186 ließ sich kompilieren; die reale Anzeige wurde nicht am Gerät verifiziert.
- Der aktuelle Nutzerbericht bewertet die Darstellung und Funktion als unzureichend.
- Kein weiteres Flashen empfohlen, bevor die Vorschau- und Regressionstests die neuen Abnahmekriterien erfüllen.

## Gerätereferenz

- Gerät: GeekMagic SmallTV Ultra
- Stock-Firmware: Ultra-V9.0.50
- zuletzt bekannte Geräte-IP: 192.168.178.70
- Standortvorgabe für Wetter: PLZ 47239, Duisburg
- Uhr-Zeitzone: Europe/Berlin

Fallout, Pip-Boy, RobCo und Vault-Tec sind Marken bzw. geschützte Inhalte ihrer Rechteinhaber. Dieses Repository ist ein unabhängiges Fanprojekt.


### Wetteranzeige

Das Register DATA wechselt zwischen einer Detailansicht für heute und einer separaten Drei-Tage-Vorschau. Die Detailansicht zeigt gefühlte Temperatur, Luftfeuchte, Wind und Böen, Niederschlag, Regenwahrscheinlichkeit, UV-Index sowie Sonnenauf- und -untergang. Die Vorschau zeigt morgen und die zwei darauffolgenden Tage mit Datum, Wetterlage, Temperaturbereich und Regenwahrscheinlichkeit. Die Ansichten wechseln automatisch im 12-Sekunden-Takt.
