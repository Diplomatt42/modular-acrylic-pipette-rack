# AI handoff: column version

This document is optional task guidance for someone deliberately asking an AI
agent to modify this package. The recipient's explicit request takes precedence.

## Design intent to preserve

- Three unique production parts: column, shelf, back panel.
- One shared shelf between adjacent compartments, N+1 shelves for N compartments.
- Open front, 3 mm nominal acrylic, flat bottom shelf on a counter.
- Repeat identical walls and shelves vertically; no separate top part.
- Four identical 50.8 mm corner columns per compartment.
- Upper/lower tab centers remain offset at shared shelves to avoid collisions.
- Finished-part DXFs, not pre-offset toolpaths. STEP assemblies preserve separate
  bodies. Current joints are locating slip fits, not positively retained joints.

## Work procedure

1. Read README.md, CUSTOMIZATION.md, ASSEMBLY.md, and both JSON inputs.
2. Make the requested change in JSON first. Update source only if new geometry
   cannot be expressed by the existing parameters. Use relative paths; never
   depend on the original author's desktop paths or an original ChatGPT session.
3. Install requirements into a virtual environment and run source/generate.py
   with a new output directory. Preserve the delivered reference revision.
4. Inspect generated/validation_report.json, or the report in your custom output.
   Report nominal collisions, topology errors, undersized bridges, units problems,
   and nesting failures. Do not suppress failed checks to ship an invalid design.
5. Review single-box and stack STEP assemblies visually. Compare the requested
   dimension to actual bounds and keep part quantities consistent with N.
6. Recheck the user's stock thickness, machine limits, kerf-compensation workflow,
   and fit coupon. Unknown measurements are unknown; do not invent measured data.
7. Deliver the three unique production DXFs, part/assembly STEP models, revised
   input JSON, source, cut list, validation report, and a concise change note.
   Keep local nested layouts separate from individual supplier DXFs.

## Example prompts a recipient can use

> Change the single-box overall height to 101.6 mm, keeping the width, depth,
> material and shared-shelf interface. Regenerate both the one-compartment and
> four-compartment assemblies, validate them, and show the resulting clear height.

> Adapt this package to my CO2 laser with a 600 x 400 mm usable bed. My acrylic
> measures 3.05 mm thick and my measured kerf is 0.15 mm. Start with a 0.20 mm
> positive slot clearance. Keep finished-part DXFs, make a fit coupon, record the
> compensation workflow, and produce bed layouts for two four-compartment racks.

> I want 100 mm of CLEAR compartment height. Compute the outside single-box height
> from the actual thickness, update the walls and stacked model, and keep the
> number of shelves at N+1.

No physical fit or load certification is implied by successful CAD validation.
