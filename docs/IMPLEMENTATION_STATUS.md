# Implementierungsstatus – 12.11.2026

## Aktueller Stand

**Build 368 erfolgreich. ESP8266-Firmware, OTA-Loader, native 240×240-Displaytests, Paketprüfung und Prüfung des gebündelten GIFs bestanden. Die RADIO-Prüfung erzwingt jetzt echte GIF-Wiedergabe ohne Cartoon-Ersatzanimation. Die Wetter-API-Einheiten sind explizit auf km/h und mm gesetzt. Hardwaretest offen.**

Aktueller Branch-Stand zum Firmware-Build: `58ef4123aaa069cf4f5cb76a8626a85a50595201`. Build 368 hat ESP8266-Firmware, OTA-Loader und Installationspaket erfolgreich erzeugt. Die native 240×240-Prüfung der final transformierten Displayseiten ist erfolgreich. Die Wetterdetailzeilen (Windrichtung/-geschwindigkeit, Böen, Niederschlag, Regenwahrscheinlichkeit/UV sowie Sonnenzeiten) liegen innerhalb des DATA-Bereichs und bestehen die Footer-Grenzprüfung. Die Vorschauen von STAT, DATA heute, 3-Tage-Vorschau und RADIO wurden aus dem Build-Artefakt geprüft. Die Wetterabfrage fordert Windgeschwindigkeit in km/h und Niederschlag in mm explizit an. Vier synthetische GIF-Konvertertests prüfen Vollbild-Mehrbildanimation, Transparenz-Flattening, Helligkeitsverlauf und die Begrenzung von 40 auf 36 Frames bei erhaltener Gesamtdauer von vier Sekunden. Der CI-Schutztest prüft flackerfreie Ausgabe vollständiger opaker Frames, das Überspringen inkompatibler Archivdateien und dass keine Ersatzanimation statt eines echten GIF-Decoders aktiv bleibt. Das Paket enthält ein 104×104-GIF mit sieben Frames und 1,32 Sekunden Animationsdauer. Das bestätigt die konvertierte Datei, nicht die Wiedergabe auf dem ESP8266. Echte Displaydarstellung, Wetterverbindung und GIF-Laufzeit bleiben Hardwaretests.

### Display und Wetter

- **STAT:** große Uhrzeit, deutscher Wochentag und Datum.
- **DATA – HEUTE:** Temperatur, Wetterlage, gefühlte Temperatur, Luftfeuchte, Wind/Böen, Niederschlag, Regenwahrscheinlichkeit, UV sowie Sonnenauf- und -untergang.
- **DATA – 3-TAGE-VORSCHAU:** getrennte Einträge für MORGEN, UEBERMORGEN und IN 3 TAGEN; jeweils Datum, deutsch übersetzte Wetterlage und Temperaturbereich in °C. Die zusätzliche Seitenüberschrift wurde entfernt, damit sie nicht mit dem ersten Prognoseeintrag kollidiert. Regenwahrscheinlichkeit pro Prognosetag steht kompakt in der jeweiligen Datumszeile (z. B. `MORGEN 13.11 // 20%`); Wetterlage und Temperaturbereich bleiben in der großen zweiten Zeile.
- **RADIO:** eigenes Animationsfenster. GIF-Inhalte bleiben auf RADIO und überlagern weder Uhr noch Wetter.

Die nativen Vorschauen aus Build 368 wurden visuell geprüft: STAT zeigt eine große, zentrierte Uhr und das deutsche Datum; DATA heute enthält alle Detailfelder; die 3-Tage-Prognose zeigt drei klar getrennte Tageszeilen; RADIO hält das GIF im eigenen Rahmen. Die Footer-Grenzprüfung wurde nach einer Korrektur der Sonnenzeiten erfolgreich bestanden. Die native Forecast-Vorschau aus Build 313 wurde ebenfalls visuell geprüft: Datumszeile inklusive Regenwahrscheinlichkeit, darunter Wetterlage und Temperaturbereich. Alle drei Einträge passen ohne Abschneiden oder Überlagerung. Build 308 enthält zusätzlich die erweiterten deutschen Wetterlagen: keine abgeschnittenen oder überlappenden Zeilen; die drei Einträge sind innerhalb der 240×240-Fläche lesbar. Die übrigen nativen Vorschauen wurden in Build 298 geprüft. Die reale Darstellung, WLAN-/Wetterdaten und GIF-Wiedergabe auf dem Gerät sind weiterhin nicht verifiziert.

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
