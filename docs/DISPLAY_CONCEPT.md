# Verbindlicher Display-Neuentwurf – Fallout 4 / Pip-Boy / RobCo

Stand: 12.11.2026  
Status: **Firmware Build 313 / Dokumentationslauf Build 314 – native Vorschau visuell geprüft; Hardwaretest offen**

## Warum der bisherige Ansatz verworfen wird

Die bisherigen Builds wurden zwar kompiliert, aber nicht mit einem echten 240×240-Rendernachweis und nicht auf dem Gerät visuell abgenommen. Ein erfolgreicher Build ist kein Beleg für Lesbarkeit oder ein funktionierendes Layout. Build 186 ist deshalb kein freigegebener Designstand.

Die Oberfläche wird nicht weiter mit zusätzlichen grünen Effekten, GIF-Overlays oder isolierten Korrekturen repariert. Der Aufbau wird neu geordnet.

## Visuelle Referenz

Die Referenz ist der Pip-Boy 3000 Mark IV aus Fallout 4 – nicht ein beliebiges Cyberpunk-Terminal.

Wesentliche Merkmale:
- monochromes Grün auf Schwarz;
- text- und zahlenorientierte Informationsdarstellung;
- klare Registerleiste und dünne Trennlinien;
- sparsame Symbole und gezielt verwendete Vault-Boy-Grafiken;
- keine dekorativen 3D-Karten, Verläufe oder übereinanderliegenden Fenster.

Die Originalentwicklung des Pip-Boy beschreibt genau diese Einschränkungen: einfache textbasierte Oberfläche, wenige Symbole und klare Segmentierung statt Ornamentik. Siehe [Design and Development of the Pip-Boy Model 3000](https://fallout-archive.fandom.com/wiki/Design_and_Development_of_the_Pip-Boy_Model_3000).

## Gemeinsame Regeln für alle Seiten

- Canvas: exakt 240×240 Pixel.
- Hintergrund: reines Schwarz.
- Palette: höchstens drei Phosphorgrün-Stufen plus Schwarz.
- Schrift: Monospace-/Bitmap-Anmutung; die Vorschau muss die tatsächlich in der Firmware verwendeten Fonts nutzen.
- Sekundärtexte mindestens 12 px; Hauptwerte 24–48 px. Kleinere Schrift ist nur für unvermeidbare Metadaten zulässig.
- Keine Textfelder über Grafiken oder Animationen.
- Keine dauerhaften Scanline-Animationen, Bildblitze oder kompletten Bildschirm-Neuzeichnungen bei jeder Datenaktualisierung.
- Bei unverfügbaren Daten: klarer Platzhalter, z. B. „--“ oder „DATEN NICHT VERFÜGBAR“; niemals Demo- oder Beispielwerte als Live-Daten ausgeben.

## Navigation

Die drei vorhandenen Seitenslots bleiben erhalten:
- STAT
- DATA
- RADIO

Die aktive Registerkarte ist klar markiert. Die Kopfzeile bleibt bei Seitenwechseln an derselben Position, damit die Oberfläche wie ein zusammenhängendes Gerät wirkt.

## Seite 1 – STAT / Uhr

Ziel: Uhrzeit auf den ersten Blick erkennbar, Datum auf einen Blick lesbar.

Layout:
- oben: Registerleiste STAT / DATA / RADIO;
- darunter: kurze Systemkennung;
- Mitte: Uhrzeit als dominierender Wert, 24-Stunden-Format;
- darunter: deutscher Wochentag und Datum;
- unten: NTP-/Zeitzonenstatus, nur wenn sinnvoll.

Keine zusätzliche Wettervorschau auf dieser Seite. Die Uhr bekommt Platz und wird nicht mit kleinen Statusfeldern überladen.

## Seite 2 – DATA / Wetter mit zwei internen Ansichten

DATA bleibt ein einziges Hauptregister, wechselt aber intern alle 12 Sekunden zwischen zwei vollständigen Ansichten. Die Hauptnavigation bleibt STAT / DATA / RADIO.

**Ansicht 1/2 – HEUTE**
- Standort 47239 / Duisburg;
- aktuelle Temperatur und Wetterlage;
- gefühlte Temperatur und Luftfeuchtigkeit;
- Windrichtung, Windgeschwindigkeit und Böen in km/h;
- aktueller Niederschlag und heutige Niederschlagswahrscheinlichkeit;
- UV-Index;
- Sonnenaufgang und Sonnenuntergang.

**Ansicht 2/2 – 3-TAGE-VORSCHAU**
- morgen, übermorgen und der dritte Folgetag;
- Datum, deutsche Wetterbeschreibung;
- Tiefst-/Höchsttemperatur in °C;
- Regenwahrscheinlichkeit pro Prognosetag steht kompakt in der Datumszeile; Wetterlage und Temperaturbereich bleiben groß und gut lesbar.

„Hoch“ und „Tief“ werden nicht als eigenständige Wetterkennzahlen verwendet. Die Vorhersage zeigt drei Folgetage zusätzlich zur separaten Heute-Ansicht. Fehlen echte Werte, werden sie als nicht verfügbar angezeigt; es gibt keine Beispieldaten im Live-Betrieb.

Die Ansichten wechseln intern alle 12 Sekunden; die drei Hauptregister bleiben unverändert.

## Seite 3 – RADIO / Animation

Ziel: eine Animation als eigenständiger Inhalt zeigen.

Layout:
- oben: Registerleiste;
- Mitte: zentrierte Animation in einem festen Sichtfenster;
- unten: kurzer Dateiname oder Archivstatus.

Die Animation darf keine Uhr- oder Wetterdaten verdecken. Keine halbtransparenten grünen Flächen oder alten GIF-Reste außerhalb des Sichtfensters. Gibt es keine gültige Animation, erscheint ein sauberer statischer RADIO-Platzhalter.

## GIF- und Animationsstrategie

Die bisherige Laufzeit-Decodierung beliebiger GIF-Dateien wird nicht weiter als Voraussetzung behandelt.

Referenz ist das u1pns-Projekt: Dort werden Bilder und GIFs im Browser konvertiert; das Gerät selbst decodiert keine JPG-/GIF-Dateien. Für unseren ESP8266 ist die Vorverarbeitung in begrenzte Einzelbilder/Sprites deshalb der bevorzugte Weg.

Vorgesehene Grenzen für den ersten Prototyp:
- fester Sichtbereich, höchstens 120×120 Pixel;
- begrenzte Bildanzahl pro Animation;
- reduzierte Farbpalette;
- definierte Bildrate und Frame-Dauer;
- Größenprüfung vor Speicherung;
- keine automatische Wiedergabe auf STAT oder DATA.

Die Grenzen werden anhand des tatsächlichen LittleFS- und Heap-Budgets festgelegt, nicht geschätzt.

## Technischer Qualitätsnachweis vor jedem neuen Firmware-Build

1. Für STAT, DATA und RADIO existiert jeweils eine vollständige Vorschau in 240×240 Pixeln.
2. Die Vorschau verwendet dieselbe Zeichenlogik und dieselben Bitmap-Fonts wie die Firmware.
3. Es werden lange deutsche Wochentage, volle Datumsangaben, fehlende Wetterdaten und leere Animation-Slots geprüft.
4. Text wird auf Abschneiden, Überlappung und Kontrast nach RGB565-Konvertierung geprüft.
5. Jede Seite wird mindestens einmal im Wechsel mit der vorherigen und folgenden Seite gerendert; es dürfen keine Bildreste stehen bleiben.
6. Unveränderte Daten führen nicht zu unnötigen Vollbild-Redraws.
7. Erst nach bestandener Vorschau folgen Build und separater Test am echten Gerät.

## Arbeitsgrundlage

Die Recherche und Bewertung vorhandener Projekte steht in [DESIGN_REFERENCE_COMPARISON.md](DESIGN_REFERENCE_COMPARISON.md).

Wichtige Referenzen:
- [iodn/geekmagic-tv-esp8266](https://github.com/iodn/geekmagic-tv-esp8266): SmallTV Ultra, echte Renderer-Vorschauen und Displaytests.
- [giovi321/smalltv-mod](https://github.com/giovi321/smalltv-mod): SmallTV Studio und fertige Theme-Beispiele.
- [u1pns/smalltv-ultra](https://github.com/u1pns/smalltv-ultra): Browser-Konvertierung von GIFs vor der Anzeige.
- [msdxlab/SmallTV-ultra-mod](https://github.com/msdxlab/SmallTV-ultra-mod): Clock-/Weather-Face, Screen-Mirror und gezielte Teilaktualisierung.
