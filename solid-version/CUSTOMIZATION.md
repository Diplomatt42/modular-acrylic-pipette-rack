# Customization and laser setup

## Change height

Edit `geometry_mm.single_box_overall_height` in `design_parameters.json`.
This is outside height of one complete box, including its two shelves.
For a 4-inch overall box, use 101.6 mm. For a desired clear opening H, use
H + 2 * stock_model_thickness. The generator updates wall height and stack pitch.

For N compartments:

- clear height = single_box_overall_height - 2 * stock_model_thickness
- repeat pitch = clear height + stock_model_thickness
- stack height = N * clear height + (N+1) * stock_model_thickness

The shared shelf DXF does not change for height-only edits.

## Adapt to a different laser or sheet

1. Read [MATERIALS_AND_CARE.md](MATERIALS_AND_CARE.md), especially before
   choosing material for regular alcohol cleaning. Confirm your machine supports
   the actual sheet material and thickness, and follow your lab's process.
   Polycarbonate/PETG substitutions need new fit and structural checks;
   do not assume acrylic laser settings or cement remain appropriate.
2. Measure actual sheet thickness at several points. Set
   `geometry_mm.stock_model_thickness` accordingly. Nominal thickness is not a
   guarantee of actual thickness or uniformity.
3. Update `laser_profile.json`: actual usable bed dimensions, edge margins,
   inter-part spacing, minimum feature limits, and `racks_to_nest`.
   Enter a bed that is no larger than the available stock. Uniform edge margins
   model edge keepouts; irregular clamps need manual layout review.
4. Measure kerf using your actual settings and record `measured_kerf_mm`.
   This field is metadata; it does not perform compensation. Apply compensation
   once in your laser software. Power, speed, focus and passes depend on the
   machine and material, and are intentionally not guessed by the generator.
5. Cut `generated/calibration/fit_ladder.dxf` and `fit_probe.dxf` from the same
   stock. Read `slot_map.csv`: slots are numbered bottom-to-top in the DXF.
   Insert the probe edge-first so stock thickness crosses the narrow dimension.
   The probe width is the side tab width; slot length is the corresponding side
   slot length. This checks fit width, not structural retention or a complete joint.
6. Select a positive slip clearance and set `joints_mm.slot_thickness_clearance`.
   Slot width = modeled sheet thickness + this clearance. Both variants use the
   same shelf outline and slot scheme with identical input settings.
7. Review the STEP models and validation report, then prototype one compartment.

Default clearance is 0.889 mm, carried over from the supplier-oriented design.
Your calibrated laser may allow a closer slip fit. Avoid claiming a friction-fit
load rating from a clearance setting; this source requires positive clearance.
The fit ladder includes 0.05, 0.10, 0.15, 0.20, 0.30, 0.50 and 0.889 mm samples.

## Change other geometry

- `body_width`: recalculates internal width and the back tab center fractions.
- `body_depth`: moves the rear columns and all rear joint slots together.
- `column_width`: controls each column and the common shelf's side joint zones,
  including in the solid version. Default is 50.8 mm. Changing it therefore also
  changes shelf slots; regenerate all interacting parts together.
- `shelf_overhang`: affects side and rear margins around the shelf slots.
- `tab_projection`: must remain below the actual stock thickness and long enough
  to seat reliably. Changing it affects the mating joint and bottom clearance.
- `corner_radius`: default 0.381 mm small fillets on cutting corners, including
  rectangular slot corners. Preserve the existing slot envelope and fit; this
  revision does not use full semicircular ends. Radius must fit every short feature.
- `side_tab_width`, `back_tab_width`, slot length clearances: change matching tab
  and slot features together. Slot length clearance is TOTAL, not per side.
- `back_tab_fractions`: advanced joint placement, relative to internal width.
  Each lower/upper edge requires two tabs; keep their slots separate.

The current solid and column packages are compatible only when their shared
geometry and joint settings match. Height-only changes keep the shelves compatible.

## What the checks do and do not prove

Checks reject open/ambiguous contours, invalid CAD solids, nominal intersections,
incorrect assembly dimensions, insufficient specified bridges, and invalid bed
layouts. They do not simulate cutting, elastic deflection, fracture, process
tolerances, friction, or tipping. Nesting can be improved manually or by a better
nesting tool; keep cut paths separate and respect gap/margin settings.

The generated `laser_layouts` folder contains multiple-part drawings for local
cutting. For SendCutSend, submit each unique DXF from `cutting` separately with the
cut-list quantities. Check current supplier guidelines before ordering; the
included legacy feature thresholds are configurable targets, not current approval.

Useful references:
- https://sendcutsend.com/guidelines/getting-started/
- https://sendcutsend.com/materials/acrylic/
- https://cadquery.readthedocs.io/
- https://ezdxf.readthedocs.io/
