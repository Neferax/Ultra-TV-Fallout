# Ultra-TV-Fallout

Fallout-/RobCo-inspiriertes UI-Projekt für die GeekMagic SmallTV Ultra.

**Zielgerät:** GeekMagic SmallTV Ultra  
**Gemeldete Firmware:** Ultra-V9.0.50  
**Designziel:** eigenständige Pip-Boy-inspirierte Ansichten auf dem vorhandenen Display, mit Erhalt der bestehenden Gerätefunktionen.

## Projektstatus

Bestandsaufnahme und Layout-Prototypen. Es wurden keine Firmwareänderungen vorgenommen und es gibt noch keinen flashbaren Build.

## Aktueller technischer Ansatz

**Stock-Firmware zuerst – kein Flashen geplant.**

Ein unabhängiges Projekt dokumentiert, dass sich bei der SmallTV-Ultra-Stock-Firmware eigene 240×240-Bilder und GIFs über die lokale HTTP-Schnittstelle hochladen und im Photo-Album-Modus anzeigen lassen. Damit könnten wir eigene Fallout-Ansichten umsetzen, ohne die Firmware zu ersetzen.

Achtung: Die dokumentierte Referenz wurde auf Ultra-V9.0.51 getestet. Unser Gerät meldet Ultra-V9.0.50. Die API muss deshalb auf unserer Version erst mit vorsichtigen Tests bestätigt werden.

- [Strategie: Stock-Firmware-Bildmodus](docs/STOCK_FIRMWARE_IMAGE_MODE.md)
- [Referenzprojekt mit dokumentierten Endpunkten](https://github.com/MacheteFlow/GeekMagic-AI-Status)

## Designziel

Die Hauptübersicht und die Wettervorhersage bekommen eigenständige Layouts innerhalb einer gemeinsamen Fallout-/RobCo-Bildsprache.

- **STAT:** Uhr, Datum, Standort und aktuelle Wetter-/Messwerte.
- **DATA / ATMOS:** mehrtägige Wettervorhersage als kompakte Datenansicht.
- Weitere Ansichten erst nach Erfassung der tatsächlich vorhandenen Firmwarefunktionen.

## Erste Layout-Mockups (240 × 240)

- [STAT – Hauptübersicht](assets/mockups/stat-overview.svg)
- [DATA / ATMOS – Wettervorhersage](assets/mockups/data-weather.svg)

Die Mockups sind statische Layoutstudien mit Platzhalterwerten, keine Firmware und keine Live-Daten.

## Dokumentation

- [Projektplan](docs/PROJECT_PLAN.md)
- [Display-Konzept](docs/DISPLAY_CONCEPT.md)
- [Firmware-Audit-Checkliste](docs/FIRMWARE_AUDIT.md)

## Sicherheitsregeln

- Keine Firmware flashen, solange der Stock-Ansatz nicht geprüft wurde.
- Vor Änderungen vorhandene Bilder und Einstellungen sichern.
- Erst lesende API-Abfragen, danach ein einzelner reversibler Bildtest.
- Keine unnötigen Uploads: Bilder cachen, um Flash-Schreibvorgänge zu begrenzen.
- Gerät nicht aus dem Internet erreichbar machen; die lokale HTTP-Schnittstelle ist unverschlüsselt und kann ohne Authentifizierung arbeiten.

Fallout, Pip-Boy, RobCo und Vault-Tec sind Marken bzw. geschützte Inhalte ihrer jeweiligen Rechteinhaber. Dieses Projekt ist ein unabhängiges Fanprojekt und keine offizielle Bethesda-Veröffentlichung.
