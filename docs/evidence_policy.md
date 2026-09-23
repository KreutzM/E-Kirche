# Evidence policy

## Current photographs
Authoritative for present-day visible exterior condition. Prefer agreement between multiple independent views.

## Historical photographs
Useful for geometry hidden today by vegetation/objects and for long-baseline proportions. They may show earlier restoration states; verify against modern evidence.

## Historical plans and drawings
Strong structural evidence, particularly for plan/section logic. They are historical documents and must not be copied blindly into a present-day reconstruction.

## Documented dimensions
Use as scale anchors with their stated scope. Interior dimensions must not be silently treated as exterior dimensions.

## Inference

Per issue #9, visual plausibility takes priority over fine metric reconstruction.
Approximation is acceptable when it preserves recognizable forms. Existing camera fits
may support comparisons but are not certification. Log qualitative review outcomes and
remaining visible differences. Do not change documentary measurements to match an artistic choice.
Inference is allowed when necessary, but must be explicit in `data/assumptions.yaml`. Confidence should be high/medium/low and supporting evidence IDs must be listed.

Each entry under `assumptions` is keyed by a stable ID and requires `value` (finite
number), `unit`, `reason`, `confidence`, `evidence_ids` (manifest or source IDs), and
`iteration`. Example schema only, not a project dimension:

```yaml
assumptions:
  example_parameter:
    value: 0.0
    unit: m
    reason: "Explain inference and distinguish it from documented measurements."
    confidence: low
    evidence_ids: [P01]
    iteration: phase_a_001
```

## Panoramas and stitched images
Use for visual evidence only unless a projection model is explicitly solved. Do not treat stitched panoramas as ordinary pinhole-camera images.
