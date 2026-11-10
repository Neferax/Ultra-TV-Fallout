# Implementierungsstatus – 10.11.2026

## Gerät
- GeekMagic SmallTV Ultra, Firmware Ultra-V9.0.50
- IP: `192.168.178.70`
- Aktuelles Theme: 7
- Freier Speicher zuletzt gemeldet: 187.916 Bytes (ca. 183,5 KiB)

## Verbindliche Displaystruktur
Eine Wetterseite, eine Uhrseite und die vorhandenen GIF-Anzeigen dazwischen. Keine neuen Seiten. Wetter- und Uhrdaten bleiben erhalten; nur die Gestaltung wird angepasst.

## Erstes Asset fertig
- Zielpfad: `/gif/spaceman.gif`
- 80×80 px, 9 Frames, 180 ms, Loop
- ca. 14 KB
- Phosphorgrün auf Schwarz
- Eigenständiges retro-futuristisches Maskottchen, kein offizieller Bethesda-Asset

## Paket erstellt
`Ultra-TV-Fallout-Installpaket.zip` enthält:
- `gif/spaceman.gif`
- `INSTALL_SPACEMAN_WINDOWS.bat`
- `README.txt`

Das Skript prüft die Erreichbarkeit und versucht ein Backup der vorhandenen GIF-Datei. Es führt bewusst keinen Upload aus, solange der tatsächliche /gif-Uploadpfad und das Multipart-Feld auf V9.0.50 nicht eindeutig bestätigt sind.

## API-Erkenntnisse
Community-Quellen dokumentieren für Stock-Ultra:
- `POST /doUpload?dir=/gif` für 80×80 Wetter-GIFs (Skill-Referenz)
- `GET /set?gif=/gif/<datei>` zum Setzen der Wetter-GIF-Animation
- `POST /doUpload?dir=/image/` für Album-Bilder
- `GET /set?img=/image/<datei>` und Theme 3 für Fotoalbum

Die Quellen widersprechen sich beim Multipart-Feldnamen (`image` vs. `file`). Deshalb keine automatisierte Schreibaktion, bis die tatsächliche Upload-Oberfläche der installierten V9.0.50 herangezogen wurde. Die Wetter-GIF-Funktion ist im Geräte-Webinterface dokumentiert. Quellen: AgentGlance API-Notizen, SmallTV Ultra Skill und GeekMagic Handbuch.

## Noch offen
1. GIF über die Geräte-Weboberfläche hochladen und Anzeige prüfen.
2. Weitere vorhandene GIFs im selben Stil vorbereiten und einzeln austauschen.
3. Wetter- und Uhrseite anhand der realen V9.0.50-Einstellungen gestalten. Keine nicht belegten Farb-/Layout-Parameter erfinden.

## Sicherheitsstatus
Keine Dateien auf dem Gerät verändert oder gelöscht, kein Theme geändert, kein Firmware-Flash. Das lokale Gerät ist für diesen Arbeitslauf nicht direkt erreichbar; die letzte bestätigte Geräteantwort stammt aus den zuvor dokumentierten Nutzerabfragen.
