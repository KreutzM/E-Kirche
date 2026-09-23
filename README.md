# Elisabethkirche Marburg — 3D-Rekonstruktion

Reproduzierbare, quellenbasierte 3D-Rekonstruktion der **Außenarchitektur** der Elisabethkirche in Marburg.

Aktueller Arbeitsstand: [PR 2 / Phase A 004](docs/iterations/phase_a_004.md),
`blender/scene/phase_a_004.blend`. Ziel gemäß [Tracking-Issue #9](https://github.com/KreutzM/E-Kirche/issues/9):
optisch plausibles texturiertes Sichtmodell. Außendetails und selbstständige prozedurale
Texturen sind enthalten. Die [interaktive Webansicht](web/README.md) enthält ein
eigenständiges GLB und eine einbettbare HTML-Seite. Die taktile Druckvorlage ist
als [spätere Aufgabe #12](https://github.com/KreutzM/E-Kirche/issues/12) vorgesehen.
[Materialien und Herkunft](docs/materials.md).

## Ziel

Ein metrisch kohärentes Blender-Modell aus frei verfügbaren Web-Ressourcen, dokumentierten Maßen,
historischen Plänen und explizit dokumentierten geometrischen Annahmen.

## Grundprinzipien

- Fakten, Quellen und Annahmen sind getrennt versioniert.
- Blender-Geometrie soll möglichst durch Python und Parameter reproduzierbar sein.
- Moderne Fotos definieren den heutigen Außenbestand.
- Historische Pläne/Fotos sind zusätzliche Evidenz, nicht automatisch der heutige Zustand.
- Jede nicht dokumentierte Dimension wird in `data/assumptions.yaml` erfasst.
- Modelländerungen werden gegen definierte Referenzansichten validiert.

## Einstieg für Astra

1. Lies zuerst `AGENTS.md`.
2. Lies `PROJECT.md`.
3. Prüfe `data/dimensions.yaml`, `data/manifest.json` und `docs/evidence_policy.md`.
4. Nutze `python scripts/validate_dataset.py`, bevor du Geometrie änderst.
5. Arbeite coarse-to-fine und dokumentiere jede neue Annahme.

## Referenzdaten

Die Binärbilder werden nicht als unkontrollierter Datenberg in Git gehalten.
`python scripts/fetch_assets.py` lädt die kuratierte freie Wikimedia-Commons-Auswahl und
schreibt aktuelle Lizenz-/Provenienzmetadaten mit.

## Schnellstart

```bash
python -m pip install -r requirements.txt
python scripts/validate_dataset.py
python scripts/fetch_assets.py --priority 1 --max-width 2500
python scripts/make_contact_sheets.py
```

Blender-Dateien und große Binärartefakte sind für Git LFS vorbereitet.

## Blender starten (auch Windows ohne PATH-Eintrag)

```bash
git lfs install --local
python scripts/run_blender.py smoke
python scripts/run_blender.py scene
```

Der Runner findet Blender im PATH oder im Windows-Standardverzeichnis. Alternativ
`--blender "C:/Pfad/blender.exe"` angeben oder `BLENDER_EXE` setzen. Der Smoke-Test
prüft CPU-Rendering und Speichern/Öffnen in `tmp/`. `scene` erstellt nur die leere
Projektszene mit Maßhilfen und verweigert das Überschreiben einer vorhandenen Szene.
Die Hallenbreite liegt auf Y, die Längsrichtung auf X. YAML wird durch das normale
Python gelesen; Blender benötigt keine zusätzlich installierten Python-Pakete.

Vor Modellierungsstart:

```bash
python scripts/validate_dataset.py --assets
python -m unittest discover -s tests -v
```

`--assets` verlangt lesbare Priority-1-Bilder; die normale Datenprüfung benötigt
keine Downloads. Der Downloader erhält bestehende Referenzen und hängt Provenienz
sowie Downloadberichte an. Wiederholungen prüfen Dateihashes; eine andere Auflösung
wird nicht über vorhandene Evidenz geschrieben. Fehler liefern einen Fehler-Exitcode.
Die Provenienz enthält Zeitpunkt, tatsächliche Download-URL und SHA-256 der lokalen
Datei; Commons-Abmessungen und Commons-SHA1 beziehen sich auf das Original.

Nach Erstellung und dokumentierter Kalibrierung der `VAL_*`-Kameras:
`python scripts/run_blender.py render`.

Prüfstand und offene Startbedingungen: [docs/readiness.md](docs/readiness.md).

## Erster Modellstand: Phase A 001

`blender/scene/phase_a_001.blend` enthält das prozedurale Grobmodell der Außenhülle:
Langhaus, Dreikonchenchor, Westtürme, Hauptdächer und Sakristei. Noch keine Fenster,
Strebepfeiler oder Schmuckdetails; die Fotokalibrierung steht aus.

```bash
python scripts/run_blender.py build --iteration phase_a_001 --assumptions data/iterations/phase_a_001_assumptions.yaml --output tmp/rebuilt_phase_a_001.blend
python scripts/run_blender.py inspect --scene tmp/rebuilt_phase_a_001.blend
python scripts/report_iteration.py
```

Voraussetzung: Priority-1-Referenzen lokal geladen. Jeder Build verlangt einen neuen
Ausgabepfad und prüft Maßanker, geschlossene Einzelmeshes und Kamera-Bildausschnitte.
Kontrollbilder und Planoverlay liegen unter `validation/renders/phase_a_001/`.
Die JSON-Berichte unter `validation/reports/phase_a_001/` werden neu erzeugt.
Die synthetischen `INSPECT_*`-Ansichten sind keine gelösten Fotokameras.

Ergebnisse, Unsicherheiten und nächste Arbeitsschritte:
[Iterationsbericht](docs/iterations/phase_a_001.md).

## Archivierter Arbeitsstand: Phase A 002 (nicht abgenommen)

`blender/scene/phase_a_002.blend` ergänzt Strebepfeiler, vertiefte Fenster und
vier provisorische Fotokameras. Die Silhouettenprüfung ist noch nicht bestanden.
Details und offene Abweichungen: [Iterationsbericht 002](docs/iterations/phase_a_002.md).

Reproduktion mit vorhandenen Referenzbildern und neuen Ausgabepfaden:

```powershell
python -m pip install -r requirements-calibration.txt
python scripts/prepare_calibration_views.py
python scripts/solve_cameras.py --assumptions data/iterations/phase_a_002_assumptions.yaml --output phase_a_002
python scripts/run_blender.py build --structure --iteration phase_a_002 --assumptions data/iterations/phase_a_002_assumptions.yaml --output tmp/rebuild_structure.blend
python scripts/run_blender.py calibrate --scene tmp/rebuild_structure.blend --cameras validation/reports/phase_a_002/camera_solutions.json --output tmp/rebuild_calibrated.blend
python scripts/run_blender.py render --scene tmp/rebuild_calibrated.blend
python scripts/photo_overlays.py phase_a_002
python scripts/run_blender.py inspect --scene tmp/rebuild_structure.blend
```

`--refine` im Kamerasolver erzeugt nur einen Höhenvorschlag; es ändert keine
Modellparameter automatisch. Fit-Residuen sind keine unabhängige Genauigkeitsmessung.
