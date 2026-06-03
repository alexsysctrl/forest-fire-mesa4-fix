# forest-fire-mesa4-fix

Updated Forest Fire notebook compatible with Mesa 4.x.

## The Problem

The original forest_fire notebook uses deprecated Mesa 2.x APIs:
- `BatchRunner` → removed in Mesa 4
- `fire.run_model()` → deprecated
- `fire.dc` → renamed to `fire.datacollector`
- `df.BurnedOut` → column is `"Burned Out"` in batch_run output

## The Fix

This repo provides a working Mesa 4.x compatible version of the forest fire example with:
- `batch_run()` instead of `BatchRunner`
- Updated DataCollector access
- Correct column names
- SolaraViz visualization

## Usage

```bash
pip install mesa[solara]
python forest_fire_m4.py
solara run app.py
```

## Credits

Created to help Mesa community fix issue #421.
