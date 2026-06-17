# CLAUDE.md — Private Health Records timeline viewer

A static, single-page site that shows eye-health reports (Posner-Schlossman syndrome)
on a date-based timeline, with tap-to-zoom, rotate, print and download. Built for showing
a specialist on a tablet/phone. Hosted on GitHub Pages.

## Files
- `index.html` — the whole app: HTML + CSS + JS (ES module). Uses PhotoSwipe v5 from CDN for the zoom viewer.
- `records.js` — **generated** data file (`window.HEALTH_DATA`). DO NOT hand-edit.
- `images/manifest.json` — **source of truth** for all record metadata + patient info.
- `images/*.jpg` — full-resolution report scans/photos.
- `images/thumbs/*.jpg` — ~700px thumbnails used on the homepage (generated).

## Data flow (IMPORTANT)
`images/manifest.json`  →  (regenerate)  →  `records.js`  →  read by `index.html`.

Edit `manifest.json` only, then regenerate `records.js`. Never edit `records.js` directly —
it is overwritten. After regenerating, **bump the cache-buster** (see below).

### Regenerate records.js (PowerShell)
```powershell
Add-Type -AssemblyName System.Drawing
$dir = "C:\Users\gogogo\source\repos\private-health-records"
$m = Get-Content "$dir\images\manifest.json" -Raw | ConvertFrom-Json
$records = foreach ($r in $m.records) {
  $img = [System.Drawing.Image]::FromFile("$dir\images\$($r.newName)")
  $w=$img.Width; $h=$img.Height; $img.Dispose()
  [ordered]@{ date=$r.date; place=$r.place; category=$r.category; test=$r.test; eye=$r.eye;
    result=$r.result; notes=$r.notes; full="images/$($r.newName)";
    thumb="images/thumbs/$($r.newName)"; w=$w; h=$h }
}
$payload=[ordered]@{ patient=$m.patient; diagnosis=$m.diagnosis; records=$records }
"// Auto-generated from images/manifest.json. Edit there and regenerate.`nwindow.HEALTH_DATA = $($payload | ConvertTo-Json -Depth 6);" | Set-Content "$dir\records.js" -Encoding utf8
```
`records.js` must carry each image's real pixel `w`/`h` — PhotoSwipe needs them for correct zoom.

## ⚠️ Image orientation — the EXIF trap (this bit us)
Phone photos carry an **EXIF orientation tag** (id 274). Two layers read it differently:
- **.NET / System.Drawing** (used for thumbnails) IGNORES EXIF — it uses raw pixels.
- **Browsers** HONOR EXIF — they rotate the image per the tag.

If you rotate the *pixels* (e.g. `RotateFlip`) but leave the EXIF tag, the thumbnail looks right
but the browser double-rotates the full image → it appears sideways in the viewer only.

**Rule:** whenever you rotate or "fix" an image, also normalise the EXIF orientation tag to 1
(or strip it). Check tags first:
```powershell
Add-Type -AssemblyName System.Drawing
Get-ChildItem "$dir\images" -Filter *.jpg | ForEach-Object {
  $i=[System.Drawing.Image]::FromFile($_.FullName); $o=0; try{$o=$i.GetPropertyItem(274).Value[0]}catch{}
  "{0,-60} {1}x{2} orient={3}" -f $_.Name,$i.Width,$i.Height,$o; $i.Dispose() }
```
Reset orientation to normal (pixels unchanged) on any file showing `orient=6/8/3`:
```powershell
$enc=[System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders()|?{$_.MimeType -eq 'image/jpeg'}
$ep=New-Object System.Drawing.Imaging.EncoderParameters(1)
$ep.Param[0]=New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality,[long]92)
$img=[System.Drawing.Image]::FromFile($path)
$pi=$img.GetPropertyItem(274); $pi.Value=[byte[]](1,0); $img.SetPropertyItem($pi)
$tmp="$path.tmp"; $img.Save($tmp,$enc,$ep); $img.Dispose(); Move-Item $tmp $path -Force
```
After fixing pixels/orientation, regenerate thumbnails (max 700px) and bump the cache-buster.

## ⚠️ Browser image cache
Image filenames are stable, so browsers keep serving the OLD cached copy even after you change
the file — a plain refresh won't update it. We cache-bust by appending `?v=<ASSET_V>` to every
image URL in `index.html`:
```js
const ASSET_V = '2026-06-17b';
DATA.records.forEach(r=>{ r.thumb += '?v='+ASSET_V; r.full += '?v='+ASSET_V; });
```
**Whenever you change any image file, bump `ASSET_V`** so browsers refetch.

## Local preview
The page is an ES module + loads CDN modules, so it MUST be served over http (not file://).
```
uv run --python 3.12 python -m http.server 8765 --directory "C:\Users\gogogo\source\repos\private-health-records"
```
Then open http://localhost:8765/  (Ctrl+C to stop).

### Deep link
`#open=N` opens report N directly in the zoom viewer (0-based, in current sort order).

## Deploy
GitHub Pages, repo `clarkz1024/private-health-records`, source = `main` branch root.
Pushing to `main` auto-rebuilds (~1 min). Public URL:
**https://clarkz1024.github.io/private-health-records/**

## 🔒 Privacy
These reports contain real PII: full name, DOB, home address, and **Medicare number**
(on the blood-test images). The repo is **public** (required for Pages on the free plan), so this
data is on the open internet by the owner's explicit choice. If asked to lock it down: redact the
Medicare number/address from images, and/or move to a password-protected host.

## Conventions
- Image filename: `YYYY-MM-DD_<Place>_<TestCategory>-<TestName>_<Eye>.jpg` (date-first → sorts chronologically).
- Eye codes: `OD` = right, `OS` = left, `OU` = both, `null` = systemic/blood.
- Categories drive the homepage filter chips and card colours; keep them consistent in `manifest.json`.
- To add/remove a report: edit `manifest.json`, add/remove the image (+ its thumbnail), regenerate
  `records.js`, bump `ASSET_V`, commit, push.
