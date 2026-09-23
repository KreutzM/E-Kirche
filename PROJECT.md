# Project specification

## Scope
Present-day **exterior** of the Elisabethkirche, Marburg.

Out of scope for the current phase:
- interior architecture;
- furnishings;
- hidden geometry without exterior relevance;
- speculative ornament for which no evidence exists.

## Acceptance priorities (tracking issue #9)

1. Convincing appearance, recognizable proportions and present-day exterior character.
2. Textured visual model; fine visual detail may use textures rather than mesh geometry.
3. Separate robust tactile version for blind pupils at about 20 cm longest extent.

Detailed metric accuracy and exhaustive camera calibration are not completion gates.
Modern photographs guide a documented visual plausibility review. Keep existing scale
anchors, coordinate conventions and evidence provenance; do not claim surveyed accuracy.

## Evidence transparency
A reviewer should be able to distinguish documented measurements, photograph/plan-supported geometry, inferred dimensions and purely visual approximations.

## Target outputs
- Blender scene in metres;
- reproducible Blender-Python generators;
- exterior mesh with named collections;
- validation renders for principal viewpoints;
- assumptions/evidence log;
- optional GLTF/OBJ exports.
- packaged textures and visual previews;
- separate printable STL and/or 3MF, with explicit scale and printing notes;
- physical test-print and tactile feedback before final tactile acceptance.

## Current phase
PR 1: finish characteristic forms and visual plausibility review.
PR 2: recognizable exterior detail, materials and textures.
PR 3: simplified tactile model, slicer checks and print handoff.
Printing process/material and the interpretation of the 20 cm target must be confirmed before PR 3.
