# Installation – GeekMagic SmallTV Ultra

## Zielgerät

Diese Installationsdateien sind für die **GeekMagic SmallTV Ultra mit ESP8266** und die Stock-Firmware `Ultra-V9.0.50` gebaut. Nicht für SmallTV Pro oder ESP32-Varianten verwenden.

## Warum zwei Dateien?

Die Stock-Firmware reserviert einen großen Teil des 4-MB-Flashs für GIFs/Bilder. Ihr OTA-Update-Slot ist zu klein für die vollständige Fallout-Firmware. Deshalb wird zuerst ein kleiner OTA-Loader installiert. Dieser startet mit einer passenden OTA-fähigen Flash-Aufteilung und nimmt anschließend die vollständige Firmware an.

## Installation über WLAN

1. Gerät eingeschaltet lassen und im Heim-WLAN betreiben.
2. Im Browser eines Geräts im selben WLAN `http://192.168.178.70/update` öffnen.
3. **`smalltv-ultra-fallout-loader.bin`** auswählen und das Update starten.
4. Warten, bis das Gerät neu gestartet ist. Der Loader hat keine Display-Oberfläche; ein dunkles Display ist währenddessen erwartbar.
5. Mit dem offenen WLAN **`SmallTV-Loader`** verbinden.
6. Im Browser `http://192.168.4.1/update` öffnen.
7. **`smalltv-ultra-fallout-firmware.bin`** auswählen und das Update starten.
8. Neustart abwarten. Danach im Router nach der neuen Geräte-IP sehen. Falls die WLAN-Verbindung nicht übernommen wurde, muss die WLAN-Einrichtung über den Setup-Zugang der Firmware erfolgen.

**Wichtig:** Die große Firmware nicht direkt in Schritt 3 hochladen. Erst den Loader installieren. Während beider Uploads und Neustarts die Stromversorgung nicht trennen.

## Gebaute Dateien

| Datei | Größe | SHA-256 |
|---|---:|---|
| Loader | 316.112 Bytes | `de86b968495f03ecb0e37edeef02247202a942d7fa96dda5534564a3eef0ab2f` |
| Fallout-Firmware | 701.600 Bytes | `9e530d102b92c251e9ed1ee36d7791077f43375d10693eff9b012619765d4df4` |

GitHub Actions Build: [Run 42805367195](https://github.com/Neferax/Ultra-TV-Fallout/actions/runs/42805367195).

## Grenzen / Wiederherstellung

- Der Build und beide Binärdateien wurden durch GitHub Actions erzeugt. Ein realer Flash- und Displaytest am Gerät wurde noch nicht durchgeführt.
- Die Original-Firmware wird durch den Wechsel ersetzt. Eine Rückkehr zur Stock-Firmware ist über den Web-Updater nicht zugesichert; dafür wäre ein vorheriges vollständiges Backup und gegebenenfalls UART-Zugriff nötig.
- Stock-GIFs werden nicht automatisch in die neue LittleFS-Struktur übernommen. Vorhandene Originaldateien separat sichern und später über die neue GIF-Uploadseite erneut hochladen.
- Die Übernahme der WLAN-Zugangsdaten ist nicht bestätigt. Nach dem Flash kann eine erneute WLAN-Einrichtung nötig sein.
- Bisher wurde am Gerät nichts geschrieben oder gelöscht.
