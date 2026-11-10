# Display-Konzept – Fallout / RobCo

## Verbindliche Bestandsstruktur

Das Gerät hat eine vorhandene Wetterseite, eine vorhandene Uhrseite und GIF-Anzeigen dazwischen. Diese Struktur bleibt bestehen. Keine zusätzlichen Seiten und kein unnötiger Firmware-Neubau.

## Gemeinsame Bildsprache

- Referenz: Fallout 4 / Pip-Boy 3000 Mark IV
- tiefschwarzer Hintergrund
- monochromes Phosphorgrün mit wenigen Helligkeitsstufen
- kompakte technische Schrift, klare Kontraste
- RobCo-Rahmen, Statusleisten und kleine technische Kennungen
- dezente Scanline-Anmutung nur, wenn sie die Lesbarkeit nicht stört
- kein starkes Flackern und keine hektischen Vollbildanimationen

## Wetterseite

Die vorhandenen Wetterdaten und deren Aktualisierung bleiben erhalten. Gestaltung:
- klare Kopfzeile im RobCo-Terminal-Stil
- aktuelle Temperatur als primärer Wert
- Wetterzustand und Symbol gut erkennbar
- weitere bereits vorhandene Messwerte in kompakten Statusfeldern
- keine erfundenen oder fest eingebrannten Live-Werte

## Uhrseite

Die vorhandene Uhr- und Datumsfunktion bleibt erhalten. Gestaltung:
- Uhrzeit als größtes Element
- Datum/Wochentag darunter
- optional bereits vorhandene Zusatzwerte in kleinen Statuszeilen
- grüne Terminal-Rahmen und dezente technische Beschriftung

## GIF-Sequenz zwischen den Seiten

- vorhandene GIF-Slots verwenden
- kurze, gut erkennbare Animationen
- möglichst 80×80 bzw. in der tatsächlich unterstützten Größe
- Schwarz/Phosphorgrün
- niedrige Dateigröße und wenige Frames
- Animationen dürfen Wetter- und Uhrdaten nicht verdecken

## Implementierungsprinzip

Erst die vorhandenen Seiten anpassen, dann GIFs einzeln ersetzen. Originaldateien sichern und jeden Schritt am Display prüfen. Keine Firmware ersetzen, solange die Stock-Firmware die benötigten Funktionen bereitstellt.

Die tatsächlichen Schreibschnittstellen der Firmware Ultra-V9.0.50 sind noch nicht vollständig verifiziert. Layoutregeln sind daher festgelegt, aber keine nicht getestete API wird als funktionsfähig ausgegeben.
