# Modular Acrylic Pipette Rack

Two customizable, laser-cut acrylic rack designs: **solid sides** and **corner
columns**. Stack identical compartments vertically while sharing one shelf at
each interface, instead of doubling the floor and ceiling.

**[Download the solid CAD package](https://github.com/Diplomatt42/modular-acrylic-pipette-rack/releases/download/v1.0/solid_version_3mm_editable_CAD_package.zip)**
| **[Download the column CAD package](https://github.com/Diplomatt42/modular-acrylic-pipette-rack/releases/download/v1.0/column_version_3mm_editable_CAD_package.zip)**
| **[Release notes](https://github.com/Diplomatt42/modular-acrylic-pipette-rack/releases/tag/v1.0)**

Each download is a complete folder with CAD, editable source, configuration,
assembly notes and an AI handoff guide. You can use the delivered DXF/STEP files
without installing the generator.

![Solid and column rack comparison](images/cost-comparison.png)

*The SendCutSend prices are supplied quotes. DIY prices in the image are estimated
acrylic stock totals for a batch of four complete racks (16 compartments), before
shipping and tax. They are not per-rack DIY prices. Get current quotes for the same
quantity and specifications when comparing fabrication options.*

## Choose a version

| | Solid sides | Corner columns |
|---|---|---|
| Side support per compartment | Two full panels | Four identical columns |
| Column width | Not applicable | 2.000 in / 50.8 mm |
| Unique production parts | Side panel, shelf, back | Column, shelf, back |
| Four-compartment quantities | 8 sides, 5 shelves, 4 backs | 16 columns, 5 shelves, 4 backs |
| Package | [solid-version/](solid-version/) | [column-version/](column-version/) |

## Dimensions and material

- Nominal material: 3 mm clear acrylic.
- Existing model thickness: 0.118 in / 2.9972 mm; customize to measured stock.
- Body width x depth: 3.500 x 11.500 in / 88.9 x 292.1 mm.
- One complete box height: 3.500 in / 88.9 mm, including both shelves.
- Clear compartment height: 3.264 in / 82.9056 mm.
- Shelf footprint: 3.750 x 11.625 in / 95.25 x 295.275 mm.
- Four-compartment overall height: 13.646 in / 346.6084 mm.
- For N compartments: N+1 shelves, N backs, and 2N sides or 4N columns.

The default laser profile assumes a 36 x 24-inch bed. Change it to match both your
actual usable laser bed and stock dimensions. DXFs use **inches**; STEP uses **mm**.

## Assemble

1. Put the first shelf flat on a level counter.
2. Insert two sides (or four columns) and one back; temporarily support the walls.
3. Cap the compartment with a second identical shelf.
4. Add the next walls onto that shared shelf and repeat.

Upper and lower wall tabs use offset slot sets, so they do not collide at shared
shelves. Follow the assembly model for front/back and top/bottom orientation.
Full instructions: [solid assembly](solid-version/ASSEMBLY.md) /
[column assembly](column-version/ASSEMBLY.md).

## Customize, or hand the package to an AI agent

Start with `AI_HANDOFF.md` in the chosen version. Edit `design_parameters.json`
for dimensions and joints, and `laser_profile.json` for bed size and cut spacing.
The JSON inputs use mm, including the box height, actual stock thickness and fit
clearances. The generator recomputes the mating parts and shared-shelf stack.

Example request:

> Change the single-box overall height to 101.6 mm, keep the shared shelf system,
> and regenerate the one-box and four-compartment STEP models and production
> DXFs. Validate the CAD and report the new clear opening height.

The source uses Python, CadQuery and ezdxf. Setup and regeneration instructions
are in each package's README. Use a new output folder to preserve earlier revisions.

| Reference | Solid | Column |
|---|---|---|
| Editable inputs and instructions | [README](solid-version/README.md) | [README](column-version/README.md) |
| AI handoff | [AI_HANDOFF.md](solid-version/AI_HANDOFF.md) | [AI_HANDOFF.md](column-version/AI_HANDOFF.md) |
| Laser customization | [CUSTOMIZATION.md](solid-version/CUSTOMIZATION.md) | [CUSTOMIZATION.md](column-version/CUSTOMIZATION.md) |
| Three production DXFs | [cutting/](solid-version/generated/cutting/) | [cutting/](column-version/generated/cutting/) |
| Individual and assembled STEP | [models/](solid-version/generated/models/) | [models/](column-version/generated/models/) |

## Prototype status and validation

**CAD-validated prototype; physical testing is still needed.** No load rating or
unlimited safe stack height is claimed. The joints are gravity-assembled locating
slip fits; they do not positively retain the stack when lifted by its top.

Checks passed for closed DXF contours, solid geometry, assembly collisions, STEP
reimport, dimensions, part quantities and bed-layout spacing. The rewritten source
also reproduces the previously shared parts. Tested customizations include height
changes and changes to stock thickness, clearance, bed size and compartment count.

Cut a fit coupon with your stock and settings, then prototype one compartment.
DXFs describe finished geometry; apply kerf compensation once in your laser CAM.
Changing the modeled thickness alone does not calibrate your laser.

See each version's `BASELINE_CHECK.json` and `generated/validation_report.json`
for the actual checks. Local nested drawings are separate from the individual
supplier DXFs and do not guarantee the fewest possible sheets.

## License and credit

Original project material is licensed under **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)**.
You can use, modify and redistribute it, including commercially, with attribution,
a license link and an indication of changes. Copyright is retained to the extent
it applies. See [LICENSE](LICENSE) and [ATTRIBUTION.md](ATTRIBUTION.md).

Third-party libraries and the SendCutSend logo/trademarks retain their own rights.
This project is not affiliated with or endorsed by SendCutSend.

## Feedback and contributions

Open an issue with your variant, stock thickness, machine/setup, changed parameters
and the problem encountered. If you submit improved geometry or instructions,
include matching source/input changes and regenerated validation results.
