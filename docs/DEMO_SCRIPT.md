# VascuLens AI — 5–7 minute live demo script

> Record this only after running the frontend and backend. The dashboard concept image is a mockup, not a recording of a running application.

## 0:00–0:40 — Introduction
“VascuLens AI is our Track A research prototype for cardiovascular risk visualization. It combines clinical tabular prediction with an interactive 3D coronary anatomy view. All scores are research-only and do not replace diagnostic imaging.”

## 0:40–1:30 — Clinical inputs
Open **Patient Inputs**. Explain that fields are generated from the trained dataset schema. Change two or three demonstration values and select **Predict CAD and vessel risk**. Show the API response and state clearly that probabilities are model estimates, not confirmed stenosis.

## 1:30–3:00 — 3D exploration
Return to **3D Coronary Explorer**. Drag the canvas to rotate the heart, use the scroll wheel to zoom, and right-drag to pan. Select LAD, LCX, and RCA in turn. Explain each artery's general perfusion territory. Point out that schematic branches inherit the parent vessel's color and that colors are linked to model probabilities only after prediction.

## 3:00–4:00 — Vessel interior
Select **Vessel interior**. Explain that this is an illustrative cross-section used to demonstrate a possible interaction pattern. Do not describe the plaque-like shape as detected or measured; the supplied clinical table does not contain a CT-derived lesion location.

## 4:00–5:20 — Metrics and interpretability
Open **Model & Evidence**. Show the measured holdout metrics and global permutation-importance table after the notebook has been run. Explain the split, CV model selection, threshold choice, leakage guard, and limitations of a 303-record dataset. Do not promise 95% accuracy unless the completed evaluation supports it.

## 5:20–6:10 — Image pathway
Briefly show the ImageCAS segmentation notebook. State that it is a separate lumen-segmentation pathway and is not fused to the clinical rows without patient-level linkage. Mention Dice/IoU as segmentation metrics, not CAD accuracy.

## 6:10–6:40 — Close
“VascuLens AI demonstrates how clinical ML outputs can be inspected in an interactive anatomical context. Next steps are anatomical mesh replacement with license documentation, external validation, expert-labeled lesion localization, and stronger explainability.”

## Before recording
- Run the backend and frontend and confirm /api/health.
- Attach the original UCI extension dataset and run the clinical notebook.
- Confirm the metrics shown are the generated outputs, not sample values.
- Avoid real patient-identifying information.
- Capture the full application window and microphone narration; export a 3–10 minute MP4 and upload to the required video platform.
