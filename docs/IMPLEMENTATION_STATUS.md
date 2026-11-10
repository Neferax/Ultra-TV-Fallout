# Implementierungsstatus – 10.11.2026

## Gerät
- GeekMagic SmallTV Ultra
- IP: `192.168.178.70`
- Firmware: `Ultra-V9.0.50`
- Aktuelles Theme laut `/app.json`: 7
- Freier Speicher laut `/space.json`: 187.916 Bytes (ca. 183,5 KiB)

## Ziel
Die bestehende Struktur bleibt erhalten: eine Wetterseite, eine Uhrseite und die GIF-Anzeigen dazwischen. Beide Seiten erhalten eine gemeinsame Fallout-4-/Pip-Boy-inspirierte Optik in Schwarz und Phosphorgrün. Keine zusätzlichen Seiten.

## Fertiges erstes Asset
- Zieldatei: `/gif/spaceman.gif`
- Auflösung: 80×80
- Animation: 9 Frames, 180 ms pro Frame, Endlosschleife
- Dateigröße: ca. 14 KB
- Stil: eigens erstelltes Retro-Terminal-Maskottchen, Phosphorgrün auf Schwarz
- Kein offizieller Bethesda-/Vault-Boy-Asset

## Noch offen
1. Upload-/Overwrite-Pfad für `/gif` auf V9.0.50 anhand der tatsächlichen Geräteoberfläche verifizieren.
2. `spaceman.gif` austauschen und Display prüfen.
3. Weitere vorhandene GIFs in derselben Bildsprache vorbereiten und einzeln ersetzen.
4. Schreibschnittstellen für Wetter- und Uhrseite der V9.0.50 verifizieren und die bestehenden Seiten anpassen, ohne Datenfunktionen zu verlieren.

## Sicherheitsstatus
Bislang wurden am Gerät keine Dateien geschrieben oder gelöscht, kein Theme geändert und keine Firmware geflasht. Wegen des begrenzten freien Speichers wird nichts zusätzlich hochgeladen, bevor der konkrete Ersetzungsweg klar ist. Originaldatei `spaceman.gif` ist laut Nutzer gesichert.
