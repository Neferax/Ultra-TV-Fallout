# Ultra-TV-Fallout – Projektplan

## Ziel
Die GeekMagic SmallTV Ultra mit Firmware **Ultra-V9.0.50** soll eine Fallout-inspirierte RobCo-/Pip-Boy-Oberfläche erhalten. Zielplattform laut bisheriger Gerätezuordnung: ESP8266 (ESP-12F), 240 × 240 Pixel, ST7789. Diese Hardwaredaten und die Firmwarekompatibilität werden vor Änderungen anhand der Originaldateien verifiziert.

## Leitlinien
1. **Bestehende Funktionen erhalten.** Uhr, Wetter, Vorhersage, Standort und vorhandene Datenquellen sollen weiter funktionieren.
2. **Keine unnötigen neuen Seiten.** Zuerst vorhandene Seiten und deren Konfigurationsmöglichkeiten inventarisieren.
3. **Jede Seite bekommt eine eigene Informationshierarchie.** Gemeinsame Fallout-Bildsprache, aber keine identischen Layouts.
4. **Stock-Firmware zuerst.** Zunächst prüfen, was V9.0.50 über Weboberfläche, Konfiguration, HTTP-Schnittstellen und Grafik-Uploads erlaubt.
5. **Keine Firmware-Experimente am Gerät, bevor ein Rückweg existiert.** Original-Firmware, Konfiguration und Wiederherstellungsweg dokumentieren.
6. **Kleine Displayfläche respektieren.** 240 × 240 Pixel; Lesbarkeit und Datenpriorität gehen vor dekorativen Effekten.
7. **Keine unbelegten Kompatibilitätsannahmen.** Änderungen werden erst nach Prüfung der konkreten Firmwaredateien umgesetzt.

## Geplanter Ablauf
### Phase 0 – Bestand sichern und analysieren
- Original-Firmware V9.0.50 beschaffen.
- Firmwaredatei, Dateigröße, Prüfsumme und Herkunft dokumentieren.
- Weboberfläche und vorhandene Displayseiten erfassen.
- Verfügbare Konfigurations- und HTTP-Schnittstellen prüfen.
- Backup- und Recovery-Verfahren festhalten.

### Phase 1 – Designsystem
- Fallout-4-Pip-Boy / RobCo als visuelle Referenz.
- Dunkler Hintergrund und monochromes Phosphorgrün.
- Gut lesbare Bitmap-/Monospace-Schrift.
- Zurückhaltende CRT-Scanlines und Glow-Effekte.
- Originale bzw. nachvollziehbar lizenzierte Grafiken; keine ungeprüfte Weiterverteilung urheberrechtlich geschützter Assets.

### Phase 2 – Vorhandene Ansichten gestalten
- Haupt-/Uhransicht: STAT-ähnliche Statusübersicht.
- Wettervorhersage: eigene DATA / ATMOS-Ansicht mit Tageszeilen und Wetter-Icons.
- Weitere vorhandene Ansichten werden erst nach der Bestandsaufnahme zugeordnet.
- Keine zusätzlichen Seiten, solange vorhandene Ansichten die Anforderungen abdecken.

### Phase 3 – Prototyp und Tests
- Layouts zunächst als statische 240 × 240-Pixel-Mockups erstellen.
- Danach auf dem tatsächlich unterstützten Anpassungsweg implementieren.
- Prüfen: Lesbarkeit, Datenaktualität, WLAN-Ausfälle, Neustart, Speicherverbrauch, Bildrate und Langzeitstabilität.
- Erst nach erfolgreichem Test auf dem Gerät installieren.

## Aktuell bekannte Ausgangslage
- Gerät: GeekMagic SmallTV Ultra.
- Weboberfläche meldet: SmallTV-Ultra, Ultra-V9.0.50.
- Repository ist zunächst leer bis auf die README.
- Die zwei vom Nutzer bereitgestellten Fotos zeigen eine farbige Haupt-/Wetteranzeige sowie eine Drei-Tage-Vorhersage.
- Die Original-Firmwaredatei liegt diesem Projekt noch nicht bei.

## Benötigter nächster Input
Die unveränderte Original-Firmware V9.0.50 als ZIP bzw. die vollständigen Herstellerdateien sowie – falls verfügbar – Screenshots der Einstellungsseiten und der Liste aller Display-Modi.