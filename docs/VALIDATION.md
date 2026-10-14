# Validation checklist

- [ ] Download/attach the original UCI Extension of Z-Alizadeh Sani dataset (303 records, target columns Cath, LAD, LCX, RCA).
- [ ] Confirm label values and class counts printed by the notebook.
- [ ] Confirm no target-related columns (Cath, CAD, LAD, LCX, RCA) are in the feature matrix.
- [ ] Run the clinical notebook from top to bottom; save the actual holdout metrics, selected models, class counts, and seed.
- [ ] Train the API model with the same source file and check /api/health, /api/schema, /api/predict, /api/metrics, and /api/explanations/global.
- [ ] Test browser rotation, zoom, pan, artery selection, vessel focus, and no-model state.
- [ ] Ensure every displayed score comes from a model response; never display demo risk percentages as actual predictions.
- [ ] Image segmentation: split by scan/patient before extracting slices; compute Dice/IoU and sensitivity; check overlays manually.
- [ ] Document dataset license and anatomical mesh license.
- [ ] Capture a real 3–10 minute demo after successful local/deployed integration.
- [ ] Keep the visible research-only/diagnostic imaging disclaimer.

The packaged frontend uses a schematic model, not a validated anatomical mesh. The image notebook is a starter and must be checked against the actual downloaded dataset layout. No clinical accuracy or image-segmentation score is claimed by the package itself.
