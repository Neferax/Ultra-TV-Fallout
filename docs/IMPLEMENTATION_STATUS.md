# Implementierungsstatus – 12.11.2026

## Aktueller Stand

**Build 340 erfolgreich. GIF-Konvertierung, drei synthetische Tests und flackerfreie Ausgabe vollständiger, opaker Frames bestätigt. Build 343 erfolgreich; Builds 344–346 prüfen das automatische Überspringen inkompatibler GIFs. Hardwaretest offen.**

Aktueller Branch-Stand: `b23b581e4eae4bf50102da3b83dda90862810f3f`. Build 340 hat Firmware und OTA-Loader erfolgreich gebaut; der CI-Schutztest bestätigt, dass vollständige opake GIF-Frames ohne vorheriges Schwarz-Löschen ausgegeben werden. Build 343 kompiliert den Quellcode mit dem neuen Ablehnungsstatus. Builds 344–346 prüfen die finale Transformation für automatisches Überspringen inkompatibler Dateien. Die finale Firmware entsteht durch mehrere Build-Transformationen; Änderungen am Player werden deshalb zusätzlich gegen den erzeugten Quellcode geprüft.

### Display und Wetter

- **STAT:** große Uhrzeit, deutscher Wochentag und Datum.
- **DATA – HEUTE:** Temperatur, Wetterlage, gefühlte Temperatur, Luftfeuchte, Wind/Böen, Niederschlag, Regenwahrscheinlichkeit, UV sowie Sonnenauf- und -untergang.
- **DATA – 3-TAGE-VORSCHAU:** getrennte Einträge für MORGEN, UEBERMORGEN und IN 3 TAGEN; jeweils Datum, deutsch übersetzte Wetterlage und Temperaturbereich in °C. Die zusätzliche Seitenüberschrift wurde entfernt, damit sie nicht mit dem ersten Prognoseeintrag kollidiert. Regenwahrscheinlichkeit pro Prognosetag steht kompakt in der jeweiligen Datumszeile (z. B. `MORGEN 13.11 // 20%`); Wetterlage und Temperaturbereich bleiben in der großen zweiten Zeile.
- **RADIO:** eigenes Animationsfenster. GIF-Inhalte bleiben auf RADIO und überlagern weder Uhr noch Wetter.

Die native Forecast-Vorschau aus Build 313 wurde visuell geprüft: Datumszeile inklusive Regenwahrscheinlichkeit, darunter Wetterlage und Temperaturbereich. Alle drei Einträge passen ohne Abschneiden oder Überlagerung. Build 308 enthält zusätzlich die erweiterten deutschen Wetterlagen: keine abgeschnittenen oder überlappenden Zeilen; die drei Einträge sind innerhalb der 240×240-Fläche lesbar. Die übrigen nativen Vorschauen wurden in Build 298 geprüft. Die reale Darstellung, WLAN-/Wetterdaten und GIF-Wiedergabe auf dem Gerät sind weiterhin nicht verifiziert.

## Recherche vorhandener SmallTV-Projekte

Die folgenden Projekte wurden als Referenzen geprüft:

- [iodn/geekmagic-tv-esp8266](https://github.com/iodn/geekmagic-tv-esp8266): explizite SmallTV-Ultra-Unterstützung, gerenderte Vorschauen mit den Firmware-Fonts und Displaytests.
- [giovi321/smalltv-mod](https://github.com/giovi321/smalltv-mod): visueller Theme-Editor SmallTV Studio und fertige 240×240-Layouts. Das Theme-Format ist nicht unmittelbar mit unserem aktuellen Firmwarezweig kompatibel.
- [u1pns/smalltv-ultra](https://github.com/u1pns/smalltv-ultra): verarbeitet Fotos und GIFs im Browser vor; reduziert damit die Last des ESP8266. Sicherheitsmodell und persönlicher Projektstatus erlauben keine ungeprüfte Übernahme.
- [msdxlab/SmallTV-ultra-mod](https://github.com/msdxlab/SmallTV-ultra-mod): Referenz für gezielte Teilaktualisierung und Screen-Mirror.

Details und technische Bewertung: [DESIGN_REFERENCE_COMPARISON.md](DESIGN_REFERENCE_COMPARISON.md).

## Designziel

Fallout 4 / Pip-Boy 3000 Mark IV: monochromes Grün auf Schwarz, klare Registerleiste, dünne Trenner, knappe deutsche Labels und wenige gezielte Grafiken. Keine Neon-Verläufe, pseudo-3D-Karten oder dekorativen Vollbild-Effekte.

Verbindliche Spezifikation und Abnahmekriterien: [DISPLAY_CONCEPT.md](DISPLAY_CONCEPT.md).

## GIF-Strategie und Grenzen

Die bisherige Laufzeit-Decodierung beliebiger GIFs auf dem ESP8266 wird nicht als uneingeschränkt belastbar vorausgesetzt. Die tatsächlichen Limits müssen am LittleFS- und Heap-Budget gemessen werden. Die aktuelle Quellcodevariante enthält einen 12-Bit-LZW-Decoder und eine Laufzeit-Heap-Prüfung; Framerate, Speicherfragmentierung, Vollständigkeit verschiedener GIFs und Darstellung auf dem Gerät sind nicht verifiziert.

## Offene Abnahme

1. Hardwaretest des aktuellen Builds auf dem SmallTV Ultra.
2. Tatsächliche Wetterdaten, fehlende Daten und Wiederverbindung auf dem Gerät prüfen.
3. GIF-Wiedergabe, Speicherverbrauch und Langzeitstabilität auf dem Gerät prüfen.
4. Erst nach diesen Prüfungen eine Hardwarefreigabe erteilen.

## Gerätestatus und Flash-Hinweis

Es liegt keine bestätigte Hardware-Abnahme für den aktuellen Branch-Stand vor. Die native Vorschau ist kein Ersatz für einen Test am physischen Display. Der aktuelle Stand ist nicht hardwareseitig freigegeben.
