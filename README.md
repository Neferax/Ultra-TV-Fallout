# Ultra-TV-Fallout

Fallout-/RobCo-inspiriertes Anpassungsprojekt für die GeekMagic SmallTV Ultra.

**Gerät:** GeekMagic SmallTV Ultra  
**Firmware:** Ultra-V9.0.50  
**Geräte-IP:** 192.168.178.70  
**Designziel:** Pip-Boy-3000-Mark-IV-Anmutung mit schwarzem Hintergrund, Phosphorgrün und gut lesbaren Originaldaten.

## Tatsächliche Displaystruktur

Die vorhandene Struktur bleibt erhalten:
- eine Wetterseite
- eine Uhrseite
- dazwischen die vorhandenen GIF-Anzeigen

Es werden keine unnötigen neuen Seiten gebaut. Wetter- und Uhrseite sollen direkt angepasst werden; die vorhandenen GIFs werden schrittweise durch kompakte Fallout-inspirierte Animationen ersetzt.

## Status

- [x] Gerät und Firmwarestand dokumentiert
- [x] Speicherstand und vorhandene GIFs erfasst
- [x] Erste 80×80-GIF erstellt: 9 Frames, 180 ms, ca. 14 KB
- [x] Austauschdatei heißt `spaceman.gif`
- [ ] Vollständiges Firmware-Redesign umgesetzt
- [ ] GIF am Gerät hochladen und Anzeige prüfen
- [ ] Stock-UI-Rendering für Wetter- und Uhrseite technisch zugänglich machen
- [ ] Wetterseite im Pip-Boy-Stil implementieren
- [ ] Uhrseite im Pip-Boy-Stil implementieren
- [ ] GIF-Seiten im selben Stil integrieren

**Wichtig:** Am Gerät wurden bislang keine Schreibzugriffe, Löschungen, Theme-Wechsel oder Firmware-Updates ausgeführt. Die lokale Upload-/Overwrite-Schnittstelle für `/gif` und die Schreibschnittstellen für die beiden Seiten sind auf Ultra-V9.0.50 noch nicht verifiziert. Deshalb wird nichts blind automatisiert.

## Asset

Die erste Animation ist ein eigens erstelltes Retro-Terminal-Maskottchen, Fallout-inspiriert, aber kein offizieller Bethesda-/Vault-Boy-Asset. Sie liegt im vorbereiteten Paket unter `gif/spaceman.gif`.

## Technische Entscheidung

Die geprüfte Alternative `smalltv-mod` ist kein Skin für die originale Ultra-Firmware: Ihr Theme-System ersetzt nur die Uhrenansicht innerhalb einer komplett anderen Firmware. Es passt nicht die native Wetterseite und den vorhandenen GIF-Ablauf der Stock-Firmware an. Deshalb wird sie nicht als vermeintlich einfache Lösung installiert. Details und die nächsten technischen Wege stehen in [Alternative-Firmware-Kompatibilität](docs/ALTERNATIVE_FIRMWARE_COMPATIBILITY.md).

## Dokumentation

- [Display-Konzept](docs/DISPLAY_CONCEPT.md)
- [GIF-Implementierung und API-Hinweise](docs/FALLOUT_GIF_IMPLEMENTATION.md)
- [Speicher- und Theme-Befunde](docs/DEVICE_STORAGE_AND_THEME_FINDINGS.md)
- [Implementierungsstatus](docs/IMPLEMENTATION_STATUS.md)

## Sicherheitsregeln

- Stock-Firmware beibehalten; kein Flashen.
- Vorhandene Originaldateien sichern.
- GIFs einzeln und reversibel ersetzen.
- Keine unbestätigten API-Aufrufe und keine Löschung ohne Backup.
- Gerät nicht aus dem Internet erreichbar machen.

Fallout, Pip-Boy, RobCo und Vault-Tec sind Marken bzw. geschützte Inhalte ihrer jeweiligen Rechteinhaber. Dieses Projekt ist ein unabhängiges Fanprojekt.
