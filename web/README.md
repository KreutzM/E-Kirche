# Webviewer

`index.html` zeigt das texturierte Außensichtmodell mit Dreh-, Zoom- und
Touchsteuerung sowie einem Regler für die Helligkeit. Der Viewer verwendet
AgX-Tonemapping und eine reduzierte Standardbelichtung, damit der Eindruck
der Blender-Vorschau näherkommt. Die exakte Wirkung hängt weiterhin von
Browser, Bildschirm und Beleuchtung des Webviewers ab.

`assets/elisabethkirche.glb` enthält Geometrie und vier gebackene
Farbbildtexturen; `assets/preview.png` ist das Vorschaubild. Es werden keine
Referenzfotos in das Modell übernommen. Der Viewer lädt die auf Version 4.3.1
festgelegte `<model-viewer>`-Bibliothek von Google; zum Anzeigen ist daher eine
Internetverbindung erforderlich.

## Lokal ansehen

Im Repo-Hauptverzeichnis:

```powershell
python -m http.server 8000
```

Dann `http://localhost:8000/web/` öffnen. Die Seite über HTTP(S) ausliefern,
nicht über `file://`. Bei Git-LFS-Checkouts zuerst `git lfs pull` ausführen,
damit die GLB-Datei wirklich vorliegt.

## In eine Website einbinden

Den Ordner `web/` vollständig auf den Webserver kopieren und als eigene Seite
verlinken oder einbetten:

```html
<iframe src="/web/" title="Elisabethkirche Marburg als 3D-Modell"
        style="width:100%;height:600px;border:0" loading="lazy"
        allow="fullscreen"></iframe>
```

Alternativ das `<model-viewer>`-Element aus `index.html` direkt in eine bestehende
Seite übernehmen und die Pfade zu GLB und Vorschaubild anpassen. Der Webserver sollte `.glb` als
`model/gltf-binary` ausliefern. Ohne externes CDN muss die Viewer-Bibliothek
separat lokal gehostet werden.

## Export erneut erzeugen

Blender 5.2 und die Python-Projektabhängigkeiten vorausgesetzt:

```powershell
python scripts/run_blender.py web-export
```

Standardquelle ist `blender/scene/phase_a_004.blend`, Ziel ist
`web/assets/elisabethkirche.glb`. Mit `--scene` und `--output` lassen sich beide
Pfade ändern. Der Export bäckt vier gemeinsame Materialmuster auf 1024²-Bilder,
skaliert die bestehenden metrischen UVs dafür und exportiert nur die Gebäude-Meshes.
Die Blender-Arbeitsdatei wird dabei nicht verändert. Eine vier Meter breite
Texturkachel wiederholt sich; an Kachel- und Bauteilgrenzen können sichtbare
Übergänge auftreten. Shader-Bump und die objektabhängige Wetterung sind im
Webmodell nur angenähert. Das GLB ist ein Sichtmodell, keine Druckvorlage.
