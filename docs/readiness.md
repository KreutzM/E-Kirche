# Startprüfung — 2026-09-19

## Auftrag und Stand

Geprüft: Projektvorgaben, alle sieben offenen GitHub-Issues #2–#8, Skripte,
CI, lokale Werkzeuge und Remote-Zugriff. Der Arbeitsbaum war zunächst sauber.
Phase A bleibt auf die heutige Außenarchitektur begrenzt. Es wurde keine
Kirchengeometrie modelliert und keine Kamera kalibriert.

Die fachliche Vorbereitung ist gut, aber noch keine abgeschlossene Evidenzprüfung:
32 kuratierte Referenzen, sechs dokumentierte Maßanker, noch keine geometrischen
Annahmen, keine Landmark-Koordinaten und keine gelösten Kameras. Die meisten Maße
sind Innenmaße; auch die rund 80 m Turmhöhe ist kein exaktes Aufmaß.
Die Abdeckungsbewertungen in `data/coverage.yaml` beschreiben die kuratierte Auswahl,
nicht eine bereits abgeschlossene Sichtprüfung sämtlicher Bilder.

## Werkzeuge und technische Änderungen

- Python 3.11, Pillow 12.2.0, PyYAML 6.0.3 verfügbar.
- Blender 5.2.1 LTS: Hintergrundbetrieb, Mesh-Erzeugung, Cycles-CPU-Rendering,
  Speichern und Wiederöffnen erfolgreich getestet. Kein GPU-Nachweis erforderlich;
  GPU-Beschleunigung wurde nicht geprüft.
- Git, GitHub CLI, SSH-Remotezugriff und Git LFS verfügbar; lokale LFS-Hooks installiert.
- Plattformunabhängiger Blender-Runner ergänzt; Windows benötigt weder `make`
  noch einen globalen Blender-PATH-Eintrag. Python-Fehler in Blender liefern Exitcode 1.
- Szenenpfade sind skriptbezogen; vorhandene Arbeitsszenen werden nicht überschrieben.
  Maßhilfen lesen `dimensions.yaml` über den Runner. Hallenbreite auf Y korrigiert.
- Download-Pipeline erhält bestehende Referenzen und Metadaten, prüft lokale Hashes,
  protokolliert tatsächliche Download-URL/Zeit und meldet Fehler durch Exitcode 1.
  Nichtfreie CC-BY-NC/ND-Varianten werden nicht mehr durch Teilstringvergleich akzeptiert.
  Bei HTTP 429 stoppt die Pipeline und lässt sich später mit Cache fortsetzen.
- Datenprüfung erweitert: Achsen/Ursprung, Quellenverweise, numerische Maße,
  Annahmenschema und View-Evidenz. `--assets` prüft die lokalen Priority-1-Bilder.
- Regressionstests und CI für Windows und Linux ergänzt.

## Noch vor geometrischer Arbeit erforderlich

1. Issues #2/#3 abschließen: Lizenzen und Plausibilität aller 32 Referenzen prüfen,
   die 22 Priority-1-Bilder laden und die Kontaktbögen sichten. Der erste reale
   Downloadversuch erhielt drei Bilder (M01, M02, M06); Wikimedia antwortete danach
   mehrfach mit HTTP 429. P01-Metadaten waren beim Einzeltest abrufbar (Public domain),
   die Plandatei wurde aber nicht heruntergeladen. Lokale Berichte und Metadaten
   sind gemäß bestehender Repository-Regel nicht versioniert. Teilkontaktbögen
   ersetzen keine vollständige Referenzgrundlage.
2. Issue #4: historischen Plan orientieren/skalieren und Außenkontur mit modernen
   Ansichten abgleichen; Wandstärken und Versätze als Annahmen dokumentieren.
3. Issues #5/#6: Grundkörper, Westwerk, Türme und Dächer modellieren.
4. Issue #7 parallel zur Grobmodellprüfung bearbeiten; für jede Fotografie eigene
   Kalibrierung dokumentieren. Mehrere Fotos einer Himmelsrichtung sind nicht
   automatisch eine gemeinsame Kamera. M08 bleibt vom normalen Pinhole-Solve ausgeschlossen.
5. Issue #8: Maßabweichungen mit begründeten Toleranzen, Landmark-/Silhouettenfehlern,
   Unsicherheiten und offenen Diskrepanzen pro Iteration berichten. Kein numerisches
   Genauigkeitsversprechen ohne entsprechende Evidenz. Details erst nach bestandener Grobprüfung.

Die direkte moderne Ostansicht und die vollständige Dachabdeckung bleiben fachliche
Lücken. Zusätzliche Software ist für den vorgesehenen manuellen/prozeduralen Ablauf
nicht nötig; ein Photogrammetriepaket ist optional und wurde nicht vorausgesetzt.
