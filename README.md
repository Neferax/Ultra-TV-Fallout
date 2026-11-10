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
- [x] Installationspaket vorbereitet
- [ ] GIF am Gerät hochladen und Anzeige prüfen
- [ ] Wetterseite im vorhandenen Theme anpassen
- [ ] Uhrseite im vorhandenen Theme anpassen
- [ ] übrige GIFs einzeln ersetzen

**Wichtig:** Am Gerät wurden bislang keine Schreibzugriffe, Löschungen, Theme-Wechsel oder Firmware-Updates ausgeführt. Die lokale Upload-/Overwrite-Schnittstelle für `/gif` und die Schreibschnittstellen für die beiden Seiten sind auf Ultra-V9.0.50 noch nicht verifiziert. Deshalb wird nichts blind automatisiert.

## Asset

Die erste Animation ist ein eigens erstelltes Retro-Terminal-Maskottchen, Fallout-inspiriert, aber kein offizieller Bethesda-/Vault-Boy-Asset. Sie liegt im vorbereiteten Paket unter `gif/spaceman.gif`.

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
