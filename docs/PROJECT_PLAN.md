# Ultra-TV-Fallout – Projektplan

## Ziel
Die GeekMagic SmallTV Ultra mit Stock-Firmware `Ultra-V9.0.50` soll eine
durchgängige Fallout-4-/Pip-Boy-/RobCo-Anzeige erhalten. Zielplattform laut
Upstream-Hardwareprüfung: ESP8266 (ESP-12F), 240×240 Pixel, ST7789.

## Verbindliche Displaystruktur
- Clock
- Weather
- GIF-Archiv

Der vorhandene Status-Seitenslot der alternativen Firmware wird als GIF-Seite
direkt nach Weather wiederverwendet. Die Seitenzahl wird nicht erhöht. Nur diese
drei Seiten sind standardmäßig aktiv.

## Leitlinien
1. Live-Uhrzeit, Datum, Wetter und WLAN-Funktion erhalten.
2. Keine unnötigen Dashboard-Seiten oder zusätzlichen Hintergrunddienste.
3. Lesbarkeit auf 240×240 Pixeln hat Vorrang vor Effekten.
4. Phosphorgrün auf tiefschwarzem Hintergrund, keine generischen Neonfarben.
5. GIF-Wiedergabe darf Feed-/TLS-Arbeit nicht destabilisieren.
6. Originaldateien sichern; kein Flashen ohne nachgewiesenen Rückweg.
7. Build- und Hardwaretests nicht als erfolgreich ausgeben, solange sie nicht
   tatsächlich bestätigt wurden.

## Bereits umgesetzt (Quellcode/Projekt)
- Stock-Firmware-Endpunkte read-only untersucht; Gerätedateien dokumentiert.
- Open-Source-Firmwarebasis mit SmallTV-Ultra-Unterstützung identifiziert.
- RobCo-/Pip-Boy-C++-Renderer-Patch für Clock und Weather erstellt.
- Standardkonfiguration auf Terminal-Theme, 20 Sekunden Seitenwechsel,
  Open-Meteo-Wetter für PLZ 47239 und Europe/Berlin mit automatischer
  Sommerzeit ausgerichtet.
- AnimatedGIF-Bibliothek für den ESP8266 speicherschonend konfiguriert.
- LittleFS-/TFT-Scanline-Player mit grüner Farbkonvertierung und schwarzem
  Transparenzhintergrund als Prototyp erstellt.
- Geschützte GIF-Uploadseite, Albumrotation und Feed-/TLS-/OTA-Speichersteuerung
  als Integrationspatch erstellt.
- GitHub-Actions-Workflow für Patch-Anwendung und PlatformIO-Build angelegt.

## Offene Arbeit
1. GitHub-Actions-Build erfolgreich bestätigen und Compilerfehler beheben.
2. Tatsächliche Decodergröße und IRAM-/DRAM-Reserve messen.
3. Offizielle Bethesda-GIFs und vorhandene Stock-GIFs auf Decoderkompatibilität
   prüfen.
4. Framerate, Seitenwechsel, NTP, Open-Meteo, TLS, OTA, Watchdog und
   Langzeitstabilität auf echter Hardware testen.
5. Exakte Boardrevision, Flashlayout, First-Flash- und Recovery-Weg verifizieren.
6. Erst danach ein flashfertiges Release-Paket erstellen.

## Bekannte Einschränkungen
- GIF-Canvas maximal 240×240 Pixel.
- Maximal 300 KiB pro Datei, bis zu zwölf Albumdateien.
- LZW-Codegröße maximal 11 Bit.
- Frames müssen das vollständige Canvas abdecken; transparente Pixel werden
  schwarz dargestellt. Alle Farben werden in Pip-Boy-Grün umgerechnet.
- Stock-GIFs und WLAN-Zugangsdaten werden nicht garantiert automatisch migriert.
- Die GIF-Dateien wurden noch nicht auf die Einschränkungen geprüft.

## Sicherheitsstatus
Am Gerät wurde nichts verändert. Kein Flashen, kein Löschen und kein
Überschreiben. Der Firmwarebuild und die Hardwarelaufzeit sind noch nicht
bestätigt; es existiert noch kein nachweislich flashfertiges Image.
