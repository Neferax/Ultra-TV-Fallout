# Display-Konzept – Fallout / RobCo

## Gemeinsame visuelle Sprache
- Canvas-Ziel: 240 × 240 Pixel (vor Implementierung verifizieren).
- Hintergrund: nahezu schwarz.
- Primärfarbe: Phosphorgrün; sekundäre Helligkeitsstufen statt vieler zusätzlicher Farben.
- Typografie: kompakte, gut lesbare Pixel- oder Monospace-Schrift.
- Linien, Klammern, Raster und kleine technische Kennungen im Stil eines RobCo-Terminals.
- Dezente Scanlines oder leichtes Leuchten nur, wenn sie die Lesbarkeit und Bildrate nicht beeinträchtigen.
- Keine dauerhafte starke Flicker-Animation.
- Kleine Pip-Boy-/Vault-Tec-Grafiken als funktionale Icons oder kurze Animationen, nicht als vollflächiger Hintergrund.

## Ansicht A – STAT / Hauptübersicht
**Ausgangsdaten der bestehenden Hauptanzeige erhalten:**
- Uhrzeit und Sekunden, sofern bereits vorhanden.
- Datum und Wochentag.
- Standort.
- Luftdruck.
- Temperatur.
- Luftfeuchtigkeit.
- Aktuelles Wettersymbol.

**Layout-Idee:**
- Kopfzeile: ROBCO INDUSTRIES bzw. STAT.
- Uhrzeit als stärkstes Element.
- Datum und Standort als kompakte Metadaten.
- Wetter- und Messwerte in klar getrennten Statusfeldern.
- Kleine technische Statusmarkierungen am unteren Rand.

Die Hauptansicht soll auf einen Blick die wichtigsten Informationen liefern. Nicht alle Werte müssen gleich groß dargestellt werden.

## Ansicht B – DATA / ATMOS / Vorhersage
**Ausgangsdaten der vorhandenen Forecast-Seite erhalten:**
- Drei vorhandene Vorhersagetage.
- Wochentag und Datum.
- Wetterzustand.
- Tiefst- und Höchsttemperatur.

**Layout-Idee:**
- Eigenständiger Kopf: DATA // ATMOS.
- Drei klar getrennte horizontale Tagesdatensätze.
- Wetter-Icons als monochrome Pixelgrafiken.
- Temperaturwerte rechtsbündig.
- Optional Regen-/Winddaten nur, falls die Firmware diese Werte tatsächlich bereitstellt und ausreichend Platz bleibt.

Die Vorhersage soll ausdrücklich anders aussehen als STAT: datenorientierte Liste statt großer Uhr-/Statuskomposition.

## Weitere mögliche Ansichten – erst nach Bestandsaufnahme
Die Menünamen MAP, INV und RADIO sind gestalterische Inspiration, keine Zusage, dass die Stock-Firmware diese Seiten besitzt oder zusätzliche Seiten unterstützt.
- MAP: Standort- oder Umgebungsinformationen, falls vorhanden.
- INV: Geräte-/Netzwerkstatus, falls zugänglich.
- RADIO: Verbindungs-/Signalstatus, falls zugänglich.

## Animationsregeln
- Animationen kurz und sparsam.
- Keine animierten Vollbild-Hintergründe.
- Wetter-Icons nur mit wenigen Frames.
- Animationen dürfen Daten nicht verdecken und müssen bei fehlenden Daten einen statischen Fallback zeigen.
- GIF-Unterstützung wird nicht vorausgesetzt; Format und Speicherbedarf hängen vom tatsächlichen Firmwarepfad ab.

## Referenz- und Asset-Rechte
Fallout, Pip-Boy, Vault-Tec und zugehörige Grafiken sind geschützte Marken bzw. urheberrechtlich geschützte Inhalte. Das Repository sollte keine aus dem Spiel extrahierten oder anderweitig geschützten Assets weiterverbreiten, solange Herkunft und Nutzungsrechte nicht geklärt sind. Für Tests können eigene Platzhaltergrafiken genutzt werden; für konkrete Assets Herkunft und Lizenz dokumentieren.