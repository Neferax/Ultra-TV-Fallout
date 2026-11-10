# Implementierungsstatus – 10.11.2026

## Gerät
- GeekMagic SmallTV Ultra, Firmware Ultra-V9.0.50
- IP: `192.168.178.70`
- Aktuelles Theme: 7
- Freier Speicher zuletzt gemeldet: 187.916 Bytes (ca. 183,5 KiB)

## Verbindliches Ziel
Eine Wetterseite, eine Uhrseite und die vorhandenen GIF-Anzeigen dazwischen. Alle drei Bestandteile sollen ein zusammenhängendes Fallout-4-/Pip-Boy-3000-Mark-IV-Design erhalten. Wetter, Uhrzeit, Datum, WLAN und der bisherige Ablauf müssen erhalten bleiben. Keine unnötigen zusätzlichen Seiten.

## Was tatsächlich umgesetzt ist
- Gerät, Firmwareversion und relevante Speicherwerte dokumentiert.
- Vorhandene GIF-Dateien und ihre Größen erfasst.
- Erste Designkonzepte und technische Bestandsaufnahme im Repository abgelegt.
- Kompatibilitätsprüfung der Alternative smalltv-mod durchgeführt.
- Ergebnis: smalltv-mods Theme-Uhr ist kein vollständiger Skin für die Stock-Wetterseite, Stock-Uhrseite und GIF-Rotation.
- Entscheidung dokumentiert: kein Loader und kein Firmware-Flash als Abkürzung.

## Was ausdrücklich NICHT fertig ist
- Kein vollständiger Fallout-Firmwarebuild.
- Keine Wetter- oder Uhrseite im Gerät geändert.
- Keine GIF-Datei am Gerät ersetzt.
- Kein Installationspaket als flashfertiges Firmwareartefakt.
- Keine Schreiboperation am Gerät ausgeführt.

## Technischer Befund
Die Stock-Firmware V9.0.50 ist als Hersteller-Binärpaket auffindbar; vollständiger Quellcode für das native Seiten-Rendering liegt bislang nicht vor. Die ausgelesenen Geräte-Endpunkte belegen Speicher- und Einstellungsdaten, aber keine unterstützte Schnittstelle zum Umbau der nativen Wetter-/Uhrgrafik.

Die Alternative smalltv-mod ersetzt die Stock-Firmware. Ihre Theme-Engine kann eine eigene Uhrenansicht mit Grafiken, Animationen, Formen, Text und begrenzten JSON-Datenquellen zeichnen, aber sie skinnt nicht die native Stock-Wetterseite und erhält nicht automatisch den Stock-GIF-Ablauf. Beim SmallTV Ultra ist die Installation außerdem zweistufig und erfordert einen Loader.

Siehe [Kompatibilitätsentscheidung](ALTERNATIVE_FIRMWARE_COMPATIBILITY.md).

## Nächster technischer Meilenstein
Eine belastbare Methode für den Zugriff auf das Rendering der Stock-Firmware finden oder eine vollständige Ersatzfirmware mit Wetter, Uhr und GIF-Karussell spezifizieren. Vor einem Ersatzfirmware-Ansatz sind Wetterdatenquelle, Speicherbudget, Animation, WLAN-Konfiguration, Recovery und die genaue ESP8266-Hardware zu prüfen.

## Sicherheit
- Kein Flashen, Löschen oder Überschreiben.
- Original-GIFs bleiben unangetastet.
- Keine unbestätigten Upload-Endpunkte automatisiert verwenden.
- Keine Behauptung eines erfolgreichen Builds ohne tatsächlichen Compile- und Validierungslauf.
