# Webviewer

`index.html` zeigt das texturierte Außensichtmodell mit Dreh-, Zoom- und
Touchsteuerung. Der Viewer nutzt neutrales Tonemapping und die eigene gerichtete
Studiobeleuchtung `assets/studio.hdr`. Sie macht die Ausrichtung der Fassaden
erkennbar; die Abschattungstextur betont Vertiefungen und Bauteilübergänge.

`assets/elisabethkirche.glb` enthält Geometrie, vier Farbbildtexturen, vier
Normalmaps für das Fugenrelief und eine gemeinsame Ambient-Occlusion-Textur;
`assets/preview.png` ist das Vorschaubild. Es werden keine
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
python scripts/validate_web_export.py
```

Standardquelle ist `blender/scene/phase_a_004.blend`, Ziel ist
`web/assets/elisabethkirche.glb`. Mit `--scene` und `--output` lassen sich beide
Pfade ändern. Neben der GLB entsteht jeweils `studio.hdr`. Der Export bäckt
Materialfarben und Tangentennormalen auf 1024²-Bilder, erhält die Materialrauheiten
und legt für die architektonische Abschattung einen separaten 2048²-UV-Atlas an.
Die metrischen Material-UVs bleiben der erste Texturkanal, der einmalige AO-Atlas
ist der zweite. Das exportierte Mesh hat fünf Materialgruppen.
Die Blender-Arbeitsdatei wird dabei nicht verändert. Eine vier Meter breite
Texturkachel wiederholt sich; an Kachel- und Bauteilgrenzen können sichtbare
Übergänge auftreten. Die objektabhängige Wetterung ist im Webmodell angenähert.
AO ist eine statische Näherung für lokale Abschattung und ersetzt keinen
vollständigen Raytracing-Renderer. Das GLB ist ein Sichtmodell, keine Druckvorlage.

Die Validierung prüft die tatsächlich eingebetteten Texturkanäle und UV-Zuordnungen
der GLB. Der kontrollierte Blender-Rückimport bestätigt die Materialien; eine
Abnahme der Browserdarstellung erfordert weiterhin einen Blick in den Webviewer.
