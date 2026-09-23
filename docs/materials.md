# Sichtmodell: Materialien und Texturherkunft

Die vier Texturmaterialien werden vollständig in `scripts/blender/50_materials.py`
als Blender-Shader erzeugt und in der `.blend` gespeichert. Es gibt keine heruntergeladenen
oder KI-generierten Bildtexturen und keine externen Bitmap-Abhängigkeiten.
Die Node-Rezepte sind projektintern erstellter Code, keine kopierten Materialpakete.
Die bestehenden Quellen-/Lizenznachweise für Referenzfotos bleiben in `sources/` erhalten;
keine fotografischen Pixel werden in das Modell eingebettet.

| Material | Umsetzung | Visuelle Referenz |
| --- | --- | --- |
| Sandstein | versetzte Quaderlagen, warme Farbvariation, feine vertiefte Fugen, großflächige Mineralvariation | M12, M16, M19 |
| Schiefer | versetzte schmale Reihen, blau-graue Variation und Fugen-Bump | M17, M18 |
| Glas | gedämpfte blau-graue Scheiben, dunkle Fugen, geringere Rauheit; bewusst opake Außenwirkung | M14, M16, M19 |
| Rote Türen | vertikale gemalte Holzgliederung und feine Fugen | M12 |

Die Uhr verwendet zusätzlich ein schlichtes dunkles Metallmaterial ohne Bildtextur.
Farben, Rauheiten, Bump-Stärken und Shaderrauschen sind künstlerische Einstellungen,
keine Materialmessungen. Mauer- und Dachreihenabstände sind als visuelle Annahmen in
`data/assumptions.yaml` erfasst. Die Projektionskoordinaten `MetricCourses` werden pro
Fläche in Modellmetern berechnet; auf geneigten Dachflächen folgen die Reihen der Neigung.
An Bauteil-/Flächenübergängen können Texturphasen wechseln. Es wird kein historisch
identischer Steinverband oder exakter Schieferdeckungsplan behauptet.

## Grenzen und Weiterverwendung

- Sichtbare Fenster besitzen Steinrahmen und vereinfachtes Maßwerk als Geometrie.
- Glas ist opak hinterlegt: kein Innenraum und keine Innenbeleuchtung sind erfunden.
- Shader-Bump verändert nur die Beleuchtung, nicht die druckbare Oberfläche.
- Procedural Nodes werden von Blender gerendert. Für einen späteren glTF-/anderen
  Materialexport müssten sie separat gebacken werden; ein solcher Export ist hier nicht enthalten.
- Die `.blend` benötigt zum Anzeigen/Rendern keine Originalfotos. Für einen Neuaufbau
  fordert der bestehende Build-Workflow weiterhin die Referenz-Asset-Prüfung an.
- `present` fügt nur für den Renderprozess einen Studioboden, Licht und Präsentationskameras
  hinzu. Diese werden nicht in die Arbeitsdatei zurückgespeichert und gehören nicht zum Gebäude.
