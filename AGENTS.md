# Elisabethkirche Marburg Reconstruction

## Mission
Reconstruct the **present-day EXTERIOR only** of the Elisabethkirche in Marburg as a visually convincing, plausible, textured Blender model. Preserve coherent overall proportions; detailed metric accuracy is not the acceptance goal (tracking issue #9). Do not model the interior.
Deliver a separate simplified tactile/print version for blind pupils, approximately 20 cm along its longest extent. Texture alone is not tactile geometry. Confirm printing process/material before finalizing printable detail sizes; physical print and tactile feedback remain part of final acceptance.

## Required reading before modeling
1. `PROJECT.md`
2. `data/dimensions.yaml`
3. `data/manifest.json`
4. `docs/evidence_policy.md`
5. `data/assumptions.yaml`
6. relevant reference/contact-sheet files

## Coordinate system
- Blender units: metres.
- X = East.
- Y = North.
- Z = Up.
- Origin = centre of the crossing at nominal floor level.
- Do not silently change this convention.

## Evidence precedence
When evidence conflicts, use this order:
1. Verified/documented dimensions in `data/dimensions.yaml`
2. Multiple mutually consistent modern photographs
3. Historical architectural plans and sections
4. Historical photographs
5. Geometric inference

Never present inferred geometry as measured geometry. Every inferred dimension must be recorded in `data/assumptions.yaml` with value, unit, reason, confidence, evidence IDs and iteration.

## Modeling order
1. footprint
2. nave / transept / triconch massing
3. west towers
4. roofs
5. buttresses
6. openings
7. tracery
8. ornament

Before decorative modeling, review massing and characteristic silhouettes against modern photographs. Document visible discrepancies; no additional quantitative camera solve or fine dimensional certification is required. Keep documented scale anchors and distinguish visual approximations from measurements.

## Reproducibility
- Prefer Blender Python for repeated/procedural geometry.
- Keep repeated architectural elements parametric where practical.
- Treat the `.blend` file as a working artifact; scripts + parameters + evidence are the reproducible source.
- Never destructively edit files under `references/`.
- Do not invent unavailable image metadata.
- Do not overwrite historical evidence to make it agree with the model.

## Collections
Use: MASSING, TOWERS, ROOFS, BUTTRESSES, OPENINGS, TRACERY, DETAIL, CAMERAS, REFERENCE.

## Validation
After a material geometry change:
1. run `python scripts/validate_dataset.py`;
2. generate/update relevant validation renders;
3. compare silhouette, vanishing structure and architectural landmarks;
4. record unresolved discrepancies;
5. update assumptions if new inferred dimensions were introduced.

Do not hide a discrepancy by changing a validation camera without documenting why.
