# Implementierungsstatus – 12.11.2026

## Aktueller Stand

**Status: Design-Neuaufbau erforderlich.** Die bisherigen Firmware-Layouts sind nicht freigegeben. Der Nutzer hat die Anzeige als unlesbar und funktional unzureichend bewertet. Ein erfolgreicher CI-Build ist kein Nachweis für ein brauchbares Display.

Build 186 (Commit e9afbe545b4e6223daa51b560f19b6ac16957910) wurde von GitHub Actions erfolgreich kompiliert. Die tatsächliche Darstellung auf dem Gerät wurde nicht verifiziert. Build 186 ist deshalb kein empfohlener Design- oder Release-Stand.

## Recherche vorhandener SmallTV-Projekte

Die folgenden Projekte wurden als Referenzen geprüft:

- [iodn/geekmagic-tv-esp8266](https://github.com/iodn/geekmagic-tv-esp8266): explizite SmallTV-Ultra-Unterstützung, gerenderte Vorschauen mit den Firmware-Fonts und Displaytests.
- [giovi321/smalltv-mod](https://github.com/giovi321/smalltv-mod): visueller Theme-Editor SmallTV Studio und fertige 240x240-Layouts. Das Theme-Format ist nicht unmittelbar mit unserem aktuellen Firmwarezweig kompatibel.
- [u1pns/smalltv-ultra](https://github.com/u1pns/smalltv-ultra): verarbeitet Fotos und GIFs im Browser vor; reduziert damit die Last des ESP8266. Sicherheitsmodell und persönlicher Projektstatus erlauben keine ungeprüfte Übernahme.
- [msdxlab/SmallTV-ultra-mod](https://github.com/msdxlab/SmallTV-ultra-mod): Referenz für gezielte Teilaktualisierung und Screen-Mirror.

Details und technische Bewertung: [DESIGN_REFERENCE_COMPARISON.md](DESIGN_REFERENCE_COMPARISON.md).

## Neuer Displayentwurf

Die drei vorhandenen Slots werden als STAT, DATA und RADIO neu gestaltet:

- STAT: große Uhrzeit, deutscher Wochentag und Datum; keine überflüssigen Zusatzfelder.
- DATA: zwei interne Ansichten im 12-Sekunden-Wechsel. HEUTE zeigt Temperatur, Wetterlage, gefühlte Temperatur, Luftfeuchte, Wind/Böen, Niederschlag, Regenwahrscheinlichkeit, UV sowie Sonnenauf-/untergang. Die zweite Ansicht zeigt die drei Folgetage mit Datum, Wetterlage, Temperaturbereich und Regenwahrscheinlichkeit. „Hoch/Tief“ als Labels entfallen.
- RADIO: eigenständiges Animationsfenster; keine GIF-Overlays auf Uhr oder Wetter.

Designreferenz ist Fallout 4 / Pip-Boy 3000 Mark IV: monochromes Grün auf Schwarz, klare Registerleiste, dünne Trenner, knappe Labels und wenige gezielte Grafiken. Keine Neon-Verläufe, pseudo-3D-Karten oder dekorativen Vollbild-Effekte.

Verbindliche Spezifikation und Abnahmekriterien: [DISPLAY_CONCEPT.md](DISPLAY_CONCEPT.md).

## GIF-Strategie

Die bisherige Laufzeit-Decodierung beliebiger GIFs auf dem ESP8266 wird nicht länger als Grundlage für die neue Lösung vorausgesetzt. Bevorzugt wird eine Vorverarbeitung im Browser zu kleinen, begrenzten Einzelbildern/Sprites. Die tatsächlichen Limits müssen am LittleFS- und Heap-Budget gemessen werden.

Die aktuelle Quellcodevariante enthält den 12-Bit-LZW-Decoder und eine Laufzeit-Heap-Prüfung; Build 186 kompiliert. Framerate, Speicherfragmentierung, Vollständigkeit verschiedener GIFs und Darstellung auf dem Gerät sind nicht verifiziert.

## Nächste technische Schritte

1. Eine native 240x240-Vorschau-/Teststrecke auf Basis des echten Firmware-Renderers und der echten Bitmap-Fonts aufsetzen. Die Screenshots müssen aus derselben Zeichenlogik wie das Gerät stammen.
2. STAT, DATA und RADIO als getrennte, vollständige Ansichten umsetzen und in der Vorschau auf Lesbarkeit, Clipping und Überlappung prüfen.
3. Deutsche Langtexte, fehlende Wetterdaten, NTP-Ausfall, leeres Animationsarchiv und Seitenwechsel testen.
4. Animationsvorverarbeitung auf dem PC/Browser implementieren und Datei-/Speichergrenzen prüfen.
5. Erst nach bestandener Vorschau einen neuen Firmware-Build erstellen; danach gesonderter Hardwaretest.

## Gerätestatus und Flash-Hinweis

Es liegt keine bestätigte Hardware-Abnahme für Build 186 vor. Der Nutzer hat das aktuelle Layout als unbrauchbar gemeldet. Deshalb wird Build 186 nicht als freigegebener Stand empfohlen und vorerst nicht weiter geflasht. Ob Build 186 bereits auf dem Gerät installiert wurde, ist nicht bestätigt.
