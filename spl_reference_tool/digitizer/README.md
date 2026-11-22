# Figure digitiser for published SPL plots

The digitiser is semi-automatic and leaves an audit trail. It extracts individual data points from scatter plots, and curves from centile charts, in published figures.

## Steps

1. `detect_axes(img)` finds the x-axis and y-axis lines automatically.
2. `detect_ticks(img, axes)` finds the tick-mark pixel positions automatically.
   - It uses outside ticks by default. Set `inside=True` for figures with inward ticks.
   - It keeps only ticks that follow a regular spacing.
3. **Analyst step.** Read the tick *labels* off the image and call `calibrate(x_pix, x_vals, y_pix, y_vals)`.
   - Log axes are supported.
   - The maximum calibration residual is reported.
4. `marker_mask(...)` then `detect_markers(...)` finds marker centroids.
   - Overlapping clusters are split by area, using the modal single-marker area and a split threshold of 1.35×.
   - Gridlines are removed only if they span at least half the plot.
5. `trace_curve(img, axes, rgb)` traces a coloured centile curve column by column.
6. `overlay(...)` writes a PNG with every detected point circled, so a human can check it against the original.

## Validation

Run `validate.py`. It tests synthetic figures in published styles where the true data are known. Results (`validation/`):

| Style | True n | Recovered | Median point error | Bin mean error (max) | Bin SD error (max) |
|---|---|---|---|---|---|
| Filled black markers | 300 | 91% | 0.021 cm | 0.038 cm | +0.026 cm |
| Hollow markers + gridlines | 300 | 91% | 0.022 cm | 0.122 cm | +0.186 cm |
| Dense grey, heavy overlap | 800 | 78% | 0.024 cm | 0.028 cm | +0.057 cm |
| Centile curves (3/50/97th) | — | — | 0.006 cm | — | — |

Interpretation of the validation:

- **Missed points.** Points hidden by near-complete overlap cannot be recovered from any image. Recovered age-bin means remain nearly unbiased.
- **SD inflation.** Recovered SDs are inflated by about 4% on average. This is because the dense centre of the cloud loses more points than the tails.
- **Consequences for analysis.**
  1. Weight by the paper's **reported n**, not by the digitised count.
  2. Treat digitised SDs as slightly conservative (wide).
  3. Prefer tabulated values whenever a paper gives them. Digitisation is for figures-only data.

## Inputs needed

The figure images must be supplied. This environment cannot download PMC figures, because the article pages and Europe PMC figure files are behind bot challenges.

The validated path is:

1. Download the figure PNG/JPG or PDF page yourself.
2. Place it in `digitizer/inputs/`.
3. Record the figure in `data/figure_queue_*.csv`.
