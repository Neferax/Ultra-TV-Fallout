# Fallout GIF plan for SmallTV Ultra V9.0.50

## New API finding

A community reverse-engineered API reference for SmallTV Ultra firmware V9.0.45 documents:

- Theme 1: Weather Clock Today
- Theme 2: Weather Forecast
- Theme 3: Photo Album
- Theme 7: Simple Weather Clock
- `/set?gif=/gif/x.gif`: show an 80×80 GIF in the weather-clock theme
- `/set?img=/image/x.jpg`: show a JPEG or GIF in Photo Album
- `/set?i_i=S&autoplay=0/1`: Photo Album slideshow settings
- `POST /doUpload?dir=/image/`: upload a file; the multipart part filename becomes the stored filename
- `POST /doUpload?dir=/gif/`: not yet explicitly confirmed in this reference; inspect device upload UI / file listing before use.

Reference: https://github.com/rovicomm/geekmagic-customdisplay/blob/ef5249f3146e46cd648379f559cabb51ef0e4779/docs/ultra-api.md

**Version caveat:** reference was tested on V9.0.45, while the user's device is V9.0.50. Only read-only endpoints have been tested on the user's device so far. Do not assume the GIF overlay endpoint works on V9.0.50 until tested.

## User's actual device observations (2026-11-10)

- IP: `192.168.178.70`
- Firmware: `Ultra-V9.0.50`
- Current theme: `7` (Simple Weather Clock)
- Filesystem total: 3,121,152 bytes
- Free: 187,916 bytes
- User has seven existing uploaded GIFs in `/image`; user explicitly says these can be replaced with Fallout-themed GIFs.

## Preferred implementation sequence

1. Keep theme 7 as the baseline initially.
2. Read `/album.json` (if available) and `/filelist?dir=/gif` without changing device state.
3. Inspect the stock image page / upload form to establish whether GIFs can be stored in `/gif` and what size constraints apply.
4. Test whether `/set?gif=/gif/<filename>` works on V9.0.50 only after identifying a suitable GIF and agreeing the test. This may let the weather-clock page keep its native clock/weather content while adding a Fallout animation.
5. If the 80×80 GIF overlay is not supported, use Theme 3 Photo Album for 240×240 Pip-Boy screens and use the documented slideshow controls only after testing.

## Asset requirements

- Main candidate: an 80×80 monochrome green Vault Boy/Pip-Boy status animation suitable for the weather-clock overlay.
- Album candidates: up to 240×240, Fallout 4 Pip-Boy 3000 Mark IV UI / status screens.
- Keep GIF loops short and low-frame-count to limit memory and flash use.
- Convert to a limited green/black palette; test at actual 240×240 device resolution.
- Use official game assets only with awareness that Fallout characters and imagery are copyrighted by Bethesda/ZeniMax. This is a personal fan-project direction, not a claim that the assets are freely licensed.

## Device safety

No writes, deletes, theme changes, uploads, or reboot requests have been made as part of this investigation. Do not delete existing files until they are backed up or exact replacements are ready and the user approves the replacement operation.
