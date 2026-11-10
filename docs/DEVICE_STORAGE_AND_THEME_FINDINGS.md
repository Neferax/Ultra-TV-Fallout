# Storage and theme findings – device 192.168.178.70

Observed on 2026-11-10 from the user's device responses:

- Model / firmware from `/v.json`: `SmallTV-Ultra`, `Ultra-V9.0.50`
- `/app.json`: `{"theme":7}`
- `/space.json`: `{"total":3121152,"free":187916}`
- `/filelist?dir=/image`: seven user-uploaded GIFs:
  - `1000042071.gif` — 282 KB
  - `1000042073.gif` — 6 KB
  - `1000042075.gif` — 28 KB
  - `1000042077.gif` — 120 KB
  - `1000042080.gif` — 94 KB
  - `1000042085.gif` — 112 KB
  - `1000042086.gif` — 175 KB

The user confirms these GIFs were uploaded by them previously and may be replaced with Fallout-themed GIFs matching the Pip-Boy 3000 Mark IV / Fallout 4 visual direction.

## Capacity calculation

- Total filesystem: 3,121,152 bytes (about 2.98 MiB)
- Free: 187,916 bytes (about 183.5 KiB)
- Used: 2,933,236 bytes (about 2.80 MiB)
- Current user GIF files sum to about 817 KB (sizes shown rounded by the device UI).

**Operational implication:** there is not enough free space to upload another large GIF before removing or replacing existing files. Community documentation indicates same-name uploads may overwrite, but this must be verified carefully on this specific V9.0.50 device before relying on it. Do not delete any original GIF until it has been backed up or the user has approved replacement of that exact file.

## Theme/API findings from community documentation

- Theme 3 = Photo Album.
- Theme 7 = Simple Weather Clock.
- `GET /set?img=/image/<filename>` selects/pins an image and requires Photo Album mode.
- `GET /set?theme=<n>` changes the theme.
- `GET /set?i_i=<seconds>&autoplay=<0|1>` is reported by one V9.0.50 community probe for album interval/autoplay; behaviour must be tested before use.
- `POST /doUpload?dir=/image/` uploads an image/GIF. Community sources disagree on multipart field name (`image` vs `file`); inspect actual stock upload form or use browser's built-in Pictures page before implementing.
- `GET /delete?file=/image/<filename>` deletes a file; do not use until backup and explicit user approval.

References:
- https://github.com/epicsagas/AgentGlance
- https://github.com/adrienbrault/geekmagic-hacs
- https://github.com/lucasfogacadj/smalltv-mascot

## Project direction

The user explicitly wants to replace their previously uploaded GIFs with Fallout GIFs in the Fallout 4 Pip-Boy 3000 Mark IV style. Keep the original firmware and preserve the built-in weather/time themes unless the user later asks otherwise.

Before any destructive operation:
1. Back up each existing GIF from the device, if an accessible download path exists.
2. Inspect actual image dimensions, frame count, duration, and file size.
3. Prepare replacement assets at 240×240 with restrained frame count and compact palette.
4. Replace one file at a time, verify display, and re-check `/space.json`.
5. Keep at least one known-good image and a recovery route.

Note: Fallout imagery and Vault Boy are Bethesda/ZeniMax intellectual property. For a personal fan project, use assets only with awareness of their copyright status; do not represent them as freely licensed or redistribute them as original work.
