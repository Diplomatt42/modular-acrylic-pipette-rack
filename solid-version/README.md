# Editable 3 mm acrylic modular box: solid-side version

This package includes finished CAD files and the editable inputs needed to change
the design. It uses two full side panels, one back panel per compartment,
and one shelf at each horizontal interface. Adjacent compartments share a shelf.

The current CAD is a gravity-assembled locating **slip fit**, not a press-fit or
positively locked assembly. Physical fit and load capacity have not been tested.

## Start here

- `generated/cutting/`: three unique, individual production DXFs.
- `generated/models/`: individual part STEP models, one complete compartment,
  and a four-compartment stack.
- `design_parameters.json`: dimensions and joint clearances, all in mm.
- `laser_profile.json`: laser bed, edge margin, spacing, and feature limits.
- `source/generate.py`: portable parametric source; no local machine paths.
- `generated/laser_layouts/`: nested DXFs for your own laser, plus placement data
  in the validation report. These contain multiple parts; do not upload them as
  individual SendCutSend parts.
- `generated/calibration/`: fit ladder and probe, with a separate slot map.
- `ASSEMBLY.md`, `CUSTOMIZATION.md`, `AI_HANDOFF.md`: assembly and editing guidance.
- `generated/cut_list.csv`: quantities for the configured compartment count.
- `generated/validation_report.json`: actual checks and remaining limitations.
- `MANIFEST.sha256`: checksums of included files.

## Default dimensions

| Dimension | Value |
|---|---|
| Body width x depth | 3.500 x 11.500 in (88.9 x 292.1 mm) |
| Single-box overall height, including both shelves | 3.500 in (88.9 mm) |
| Clear compartment height | 3.264 in (82.9056 mm) |
| Clear compartment width | 3.264 in (82.9056 mm) |
| Shelf footprint | 3.750 x 11.625 in (95.25 x 295.275 mm) |
| Four-compartment overall height | 13.646 in (346.6084 mm) |
| Column width / side joint zone width | 2.000 in (50.8 mm) |
| Nominal stock | 3 mm acrylic |
| Thickness used by existing CAD | 0.118 in (2.9972 mm) |
| Slot thickness width | 0.153 in (3.8862 mm) |

The 0.0028 mm difference between nominal 3 mm and the existing model is retained
to reproduce the already shared CAD. Set `stock_model_thickness` to your measured
sheet thickness when customizing; dependent dimensions are recalculated.

## Regenerate

Use Python 3.11 or 3.12 in a fresh virtual environment. The pinned dependencies
match the generator's tested environment. CAD dependencies are downloaded by pip;
they are not bundled in this ZIP.

Windows:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python source/generate.py --output generated_custom
```

macOS / Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python source/generate.py --output generated_custom
```

Edit the two JSON inputs first. The output directory must be new or empty; this
preserves previous revisions and prevents obsolete nested sheets from lingering.
Alternative inputs can be supplied with `--config` and `--laser-profile`.

## File units and compensation

Production and calibration DXFs are R2010, 1:1 **inch** units, using only LINE and
ARC cutting entities on layer 0. STEP models use **mm**. If an importer ignores DXF
units, select inches: the shelf is 3.750 x 11.625 inches, not millimetres.

These DXFs describe the desired finished geometry, not kerf-offset toolpaths.
`measured_kerf_mm` records your measurement; it does not offset the files. Let your
laser CAM compensate once, with the correct inside/outside direction. Cutting
on the line without compensation changes outside dimensions and slot widths.

## Quantity rule

For N compartments: N+1 shelves, N backs, and 2N side panels. Four compartments
therefore use five shelves. Increasing the count does not duplicate an interface.

## Validation and limits

The generator audits DXF contours, imports the actual DXFs into CAD, validates
solid geometry, checks nominal body collisions, reimports assembly STEP files,
checks envelopes and bottom position, and verifies nesting bounds and spacing.
Feature-limit checks use editable targets in `laser_profile.json`; they are not
a blanket approval for any supplier, machine, thickness, or load.

Default nesting is conservative bounding-box packing. It does not prove the
fewest possible sheets. Fit-ladder parts are extra and are not included in the
production cut list or nested layouts. Save scraps for them.

Large stacks, heavier contents, altered height, narrower columns, and tighter
fits need physical evaluation. The floor is flat on the counter only if its tabs
remain shorter than the actual material thickness. Inspect regenerated previews
or STEP models and cut a coupon before a production batch.

The original `modular_acrylic_box_rev4_1p6mm_CAD_package (1).zip` is historical:
it used separate top/floor pieces, 1.6 mm stock, and solvent-weld assembly. This
package replaces that geometry with the current shared-shelf 3 mm design; do not
mix the old parts or assembly instructions into this revision.

`reference_previews/` contains images of the delivered default revision. The generator does not regenerate these images; inspect customized STEP models separately.

## License

Original package material is licensed CC BY 4.0. Commercial reuse is permitted with attribution, a license link and change notices. See LICENSE and ATTRIBUTION.md. Third-party dependencies retain their own licenses.
