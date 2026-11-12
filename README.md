# Ultra-TV-Fallout

Fallout-4-/Pip-Boy-Oberfläche für die GeekMagic SmallTV Ultra (ESP8266, ST7789, 240x240).

> **Status: Build 368 erfolgreich; native 240×240-Vorschauen und Paketprüfungen bestanden. Hardwaretest weiterhin offen.** Die aktuelle Wetteransicht zeigt Temperatur, Wetterlage sowie gefühlte Temperatur, Luftfeuchte, Wind, Böen, Niederschlag, Regenwahrscheinlichkeit, UV und Sonnenzeiten. Die separate Drei-Tage-Vorschau ist auf zwei große Zeilen pro Tag reduziert. STAT und RADIO bleiben eigenständige Seiten. Eine Prüfung auf dem echten Gerät steht noch aus; Build 368 ist daher noch keine Hardwarefreigabe.

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

- Build 368: ESP8266-Firmware und OTA-Loader erfolgreich kompiliert; das Installationspaket wurde heruntergeladen und auf enthaltene Dateien geprüft.
- Native Vorschauen für STAT, DATA heute, DATA 3-Tage und RADIO wurden in 240x240 Pixeln geprüft.
- Das Paket enthält ein separates Vault-Boy-GIF (104×104, sieben unterschiedliche Frames, Endlosschleife). Die RADIO-Seitenvorschau ist kein Nachweis der Animation auf dem Gerät.
- Die heutige Wetterseite zeigt gefühlte Temperatur, Luftfeuchte, Wind, Böen, Niederschlag, Regenwahrscheinlichkeit, UV und Sonnenauf/-untergang.
- Die Drei-Tage-Vorschau zeigt Datum, Wetterlage, Temperaturbereich und Regenwahrscheinlichkeit je Tag.
- Die Firmware wurde nicht auf dem echten Gerät verifiziert. GIF-Laufzeit, WLAN-/Wetterabruf und Langzeitstabilität bleiben Hardwaretests; keine Hardwarefreigabe.

## Gerätereferenz

- Gerät: GeekMagic SmallTV Ultra
- Stock-Firmware: Ultra-V9.0.50
- zuletzt bekannte Geräte-IP: 192.168.178.70
- Standortvorgabe für Wetter: PLZ 47239, Duisburg
- Uhr-Zeitzone: Europe/Berlin

Fallout, Pip-Boy, RobCo und Vault-Tec sind Marken bzw. geschützte Inhalte ihrer Rechteinhaber. Dieses Repository ist ein unabhängiges Fanprojekt.


### Wetteranzeige

Das Register DATA wechselt alle 12 Sekunden zwischen der Detailansicht für heute und einer separaten Drei-Tage-Vorschau. Heute werden gefühlte Temperatur, Luftfeuchte, Wind und Böen, Niederschlag, Regenwahrscheinlichkeit, UV-Index sowie Sonnenauf- und -untergang angezeigt. Die Vorschau zeigt morgen und die zwei darauffolgenden Tage mit Datum, Wetterlage und Temperaturbereich.
