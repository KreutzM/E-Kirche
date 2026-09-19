# Elisabethkirche Marburg — 3D-Rekonstruktion

Reproduzierbare, quellenbasierte 3D-Rekonstruktion der **Außenarchitektur** der Elisabethkirche in Marburg.

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
python scripts/run_blender.py build --output tmp/rebuilt_phase_a_001.blend
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
