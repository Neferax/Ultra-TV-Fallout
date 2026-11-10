# Firmware-Audit – SmallTV Ultra V9.0.50

## Status
**Noch nicht auditiert.** Es liegt derzeit keine Original-Firmwaredatei und kein Quellcode der installierten V9.0.50 in diesem Repository vor. Deshalb sind Aussagen über interne Seitendarstellung, Theme-Hooks, API-Endpunkte und Flash-Layout vorerst offen.

## Prüfpunkte
### 1. Originaldateien
- [ ] Originalpaket vom Hersteller beschaffen.
- [ ] Dateinamen, Version und Herkunft dokumentieren.
- [ ] SHA-256-Prüfsummen erfassen.
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