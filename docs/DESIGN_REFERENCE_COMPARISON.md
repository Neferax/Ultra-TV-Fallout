# Design-Neuaufbau: Vergleich vorhandener SmallTV-Projekte

Stand: 12.11.2026

## Ergebnis der Recherche

Es wurde kein fertiges Fallout-/Pip-Boy-Firmwareprojekt speziell für das GeekMagic SmallTV Ultra gefunden. Es gibt aber mehrere echte Projekte für dieselbe Geräteklasse, aus denen sich belastbare Teile übernehmen lassen.

| Projekt | Was bereits vorhanden ist | Was wir davon verwenden | Was wir nicht blind übernehmen |
|---|---|---|---|
| [iodn/geekmagic-tv-esp8266](https://github.com/iodn/geekmagic-tv-esp8266) | SmallTV-Ultra-Unterstützung, Clock-/Weather-/Status-Seiten, Feed-Verwaltung, echte 240×240-Renderer-Vorschauen und Displaytests | Referenz für Display-Rendering, Vorschau- und Regressionstests; Grundlage für einen möglichen Firmware-Baseline-Wechsel | Das generische Smart-Clock-Layout ist nicht das gewünschte Fallout-Design; die Firmware hat keine fertige Pip-Boy-Ansicht |
| [giovi321/smalltv-mod](https://github.com/giovi321/smalltv-mod) und [SmallTV Studio](https://giovi321.github.io/smalltv-studio/) | Browser-Editor für 240×240-Themes, Ebenen für Text, Bild, Animation und Formen; fertige Beispiele Pixel Room, Terminal Ops und Live Status | Layout- und Animationsreferenz; die vorhandene Terminal-Ops-Struktur als Ausgangspunkt für ein klares Datenlayout | .stheme-Pakete sind für die Theme-Engine dieser Firmware bestimmt und nicht direkt mit der aktuellen Fallout-Firmware kompatibel. Beim SmallTV Ultra ist außerdem ein separater Loader-Installationsweg beschrieben |
| [u1pns/smalltv-ultra](https://github.com/u1pns/smalltv-ultra) | Firmware explizit für SmallTV Ultra; Clock, Wetter, Forecast, Album; Fotos und GIFs werden im Browser konvertiert, das Gerät decodiert keine JPG-/GIF-Dateien | Das Prinzip der Vorverarbeitung im Browser übernehmen, um den ESP8266 von komplexer GIF-LZW-Decodierung zu entlasten | Die veröffentlichte Firmware ist als persönliches Experiment deklariert und dokumentiert gemeinsame Standard-Zugangsdaten sowie unverschlüsseltes HTTP. Diese Sicherheitsentscheidungen werden nicht übernommen |
| [msdxlab/SmallTV-ultra-mod](https://github.com/msdxlab/SmallTV-ultra-mod) | Fork von smalltv-mod mit Clock-/Weather-Ansicht, Screen-Mirror, datenabhängigem Teil-Redraw und Fixes gegen permanentes Flackern | Referenz für gezielte Teilaktualisierung und Bildschirmspiegelung | Claude-/Codex-Meter und zugehörige PC-Daemons sind für dieses Projekt nicht erforderlich |

## Technische Entscheidung

Die bisherige Lösung bleibt nicht der Maßstab. Der nächste Entwurf wird nicht mehr nur durch erfolgreiche Kompilierung bewertet.

1. Die Display-Ansichten werden als echte 240×240-Vorschau gerendert. Dafür dienen die Renderer-Tests und Bitmap-Font-Vorschauen aus dem iodn-Projekt als Qualitätsreferenz.
2. Für den Fallout-Look dienen die klaren, textorientierten Pip-Boy-Ansichten und die vorhandenen SmallTV-Theme-Beispiele als Strukturreferenz.
3. GIFs werden vorzugsweise außerhalb des ESP8266 in begrenzte Einzelbilder/Sprites konvertiert. Auf dem Gerät soll kein beliebig großer 12-Bit-LZW-Decoder laufen müssen.
4. Firmware-Basis und Datenfunktionen werden vor einer Migration einzeln verglichen. Ein komplettes Fremd-Firmware-Image wird nicht ungeprüft über die bestehende Installation geschrieben.

## Designprinzipien für die neue Oberfläche

- Schwarzer Hintergrund und monochromes Phosphorgrün; maximal drei Helligkeitsstufen.
- Keine Neon-Verläufe, keine pseudo-3D-Karten, keine dekorativen Vollbild-Animationen und keine permanenten Scanline-Effekte.
- Klare Pip-Boy-Register am oberen Rand: STAT, DATA, RADIO.
- Dünne Trennlinien und Klammern wie in der Originaloberfläche; keine überflüssigen Rahmen.
- Zeit, Temperatur und Wetterzustand sind die größten Werte. Beschriftungen bleiben groß genug, um aus normalem Betrachtungsabstand lesbar zu sein.
- Animationen bleiben auf RADIO beschränkt und überdecken weder Kopfzeile noch Statuszeile.
- Bei fehlenden Daten erscheinen klare Platzhalter wie -- oder NO SIGNAL; keine erfundenen Live-Werte.

## Abnahmekriterien

Ein neuer Build gilt erst als Kandidat für den Gerätetest, wenn alle Punkte erfüllt sind:

- Für STAT, DATA und RADIO existieren vollständige 240×240-Render-Vorschauen aus derselben Renderlogik wie die Firmware.
- Keine abgeschnittenen Texte, überlappenden Elemente oder überzeichneten Bereiche bei langen deutschen Wochentagen und fehlenden Wetterdaten.
- Wetterwerte, Datum und Uhrzeit sind echte Daten oder klar erkennbare Platzhalter.
- Der Wechsel zwischen STAT, DATA und RADIO hinterlässt keine Bildreste.
- GIF-/Sprite-Wiedergabe läuft ohne Vollbild-Overlay und ohne blockierende Decoder-Last.
- Der Build- und Speichertest ist erfolgreich; der tatsächliche Displaytest wird separat dokumentiert.

## Quellen

- Pip-Boy-UI-Entwicklung: https://fallout-archive.fandom.com/wiki/Design_and_Development_of_the_Pip-Boy_Model_3000
- SmallTV Renderer und Vorschau: https://github.com/iodn/geekmagic-tv-esp8266
- SmallTV Studio und Theme-Beispiele: https://github.com/giovi321/smalltv-mod
- Browser-Konvertierung von GIFs: https://github.com/u1pns/smalltv-ultra
- Clock-/Weather-Redraw und Screen-Mirror: https://github.com/msdxlab/SmallTV-ultra-mod
