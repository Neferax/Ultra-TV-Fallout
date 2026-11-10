# Firmware-Audit – SmallTV Ultra V9.0.50

## Status

**Teilweise recherchiert, Binärpaket noch nicht lokal analysiert.**

Der Hersteller veröffentlicht für V9.0.50 ein Firmwarepaket:
- [FW-Smalltv-Ultra-V9.0.50.zip](https://github.com/GeekMagicClock/smalltv-ultra/blob/main/Ultra-V9.0.50/FW-Smalltv-Ultra-V9.0.50.zip)
- [Hersteller-Changelog](https://github.com/GeekMagicClock/smalltv-ultra/blob/main/Ultra-V9.0.50/update_history.txt)

Das veröffentlichte ZIP ist laut GitHub-Dateiliste 364.219 Bytes groß. Das Repository enthält an dieser Stelle ein Firmwarepaket und ein Changelog; daraus folgt nicht, dass der Firmware-Quellcode offenliegt.

Das Changelog bestätigt für ältere 9.0.x-Versionen unter anderem GIF-Wiedergabe-Optimierungen, ein Photo-Album-Thema und Wettervorhersage-Funktionen. Für V9.0.50 werden manuelle/automatische Zeitzone und eine Korrektur der Sommerzeit-Synchronisierung genannt. Es warnt außerdem in V9.0.18 vor möglichem Neustart bei Theme-Loops wegen des knappen RAM. Das ist ein konkreter Grund, Animationen und Seitenwechsel ressourcenschonend zu planen.

**Noch nicht verifiziert:** interne Seitenarchitektur, Theme-Format, HTTP-Endpunkte, Upload-Formate und die Möglichkeit, native Wetter-/Uhrseiten in V9.0.50 direkt umzubauen.

## Prüfpunkte

### 1. Originaldateien
- [x] Offizielles V9.0.50-Paket und Hersteller-Changelog gefunden.
- [ ] Originalpaket herunterladen und unverändert als Analysegrundlage sichern.
- [ ] Dateinamen, Dateigröße, Prüfsumme und Herkunft dokumentieren.
- [ ] Dateiformat und enthaltene Partitionen identifizieren.
- [ ] Prüfen, ob Quellcode, Web-Assets oder nur Binärdateien enthalten sind.

### 2. Gerät und Laufzeit
- [ ] Exakte Hardwarevariante und Displaycontroller verifizieren.
- [ ] Flash-Größe und Partitionierung aus Originaldateien ermitteln.
- [ ] RAM-/Heap-Reserven und verfügbare Dateisystembereiche bestimmen, soweit zugänglich.
- [ ] Aktuelle Gerätekonfiguration sichern.

### 3. Stock-Webinterface und Schnittstellen
- [ ] Vorhandene Seiten/Display-Modi auflisten.
- [ ] Einstellmöglichkeiten je Seite erfassen.
- [ ] Unterstützte Upload-Formate für Bilder/Animationen ermitteln.
- [ ] Dokumentierte HTTP-Endpunkte und Authentifizierung prüfen.
- [ ] Prüfen, ob Seitenlayout, Farben, Fonts und Icons konfigurierbar sind.
- [ ] Keine nicht dokumentierten Schreiboperationen ohne Backup testen.

### 4. Umsetzungsentscheidung

**Pfad A – Stock-Firmware anpassen**  
Bevorzugt, wenn die vorhandene Firmware ausreichend Layout-/Theme-Anpassung erlaubt.

**Pfad B – Ergänzende Web-/Asset-Konfiguration**  
Nur wenn diese Schnittstelle in V9.0.50 tatsächlich vorhanden und sicher nutzbar ist.

**Pfad C – Alternative Firmware**  
Nur wenn A und B nachweislich nicht ausreichen. Vorher Recovery, Original-Backup und Kompatibilität verifizieren.

## Sicherheitsregeln
- Keine Firmware flashen, bevor ein belastbarer Recovery-Weg vorliegt.
- Keine Originaldateien überschreiben.
- Änderungen zuerst auf einem separaten Branch entwickeln.
- Firmwareversion und Hardwarevariante vor jeder Build-Auswahl prüfen.
- Nach jeder Änderung Bootverhalten, WLAN, Uhrzeit, Wetter und Forecast testen.
