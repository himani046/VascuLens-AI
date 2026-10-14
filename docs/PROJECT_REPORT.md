# VascuLens AI — Track A Project Report

## 1. Problem and objective

VascuLens AI explores a multimodal interface for cardiovascular risk visualization. It pairs clinical-feature classification with an interactive 3D coronary viewer so that model outputs can be inspected alongside LAD (left anterior descending), LCX (left circumflex), and RCA (right coronary artery) summaries. The application is a research prototype, not a clinical diagnostic system.

## 2. Dataset and leakage prevention

The intended tabular source is the UCI Machine Learning Repository's *Extension of Z-Alizadeh Sani dataset* (dataset 411; 303 records; CC BY 4.0). It includes demographic, examination, ECG, laboratory, echocardiographic, and angiography-derived labels. Cath/CAD, LAD, LCX, and RCA are outcome columns, not input features. The training script excludes all of them from each model's feature matrix. This is essential because allowing the other artery labels into a model would leak direct outcome information. The original workbook is not distributed with this code; obtain it from UCI and record the exact source version used.

Categorical values are imputed and one-hot encoded inside a scikit-learn pipeline; numeric values are median-imputed and standardized. The four outcomes are trained independently. Target label mapping recognizes CAD/Normal and Stenotic/Normal; unknown labels trigger an error instead of silent guessing.

## 3. Predictive methodology and evaluation

For each available target, the pipeline creates a stratified 80/20 train/holdout split. Candidate models (Logistic Regression, RBF SVM, Extra Trees, Random Forest) are compared using stratified cross-validation on the training portion only, with ROC-AUC as the model-selection score. A decision threshold is selected using training-only out-of-fold predictions by balanced accuracy. The chosen pipeline is refit on the training portion and evaluated on the holdout once.

Reported metrics include accuracy, balanced accuracy, precision, sensitivity/recall, specificity, F1, ROC-AUC, average precision, Brier score, and the confusion matrix. The clinical model notebook prints the results and saves JSON/CSV metrics and a joblib bundle. **No result should be copied into the submission until the original dataset has been attached and the notebook has completed successfully.** No 95% target is guaranteed. With only 303 records, a single holdout estimate has substantial uncertainty; external validation and confidence intervals are desirable.

## 4. Interactive 3D visualization

The React Three Fiber viewer supports orbit rotation, zoom, pan, selection of LAD/LCX/RCA, pulse animation, and a vessel-interior illustrative view. Each major vessel and its schematic branches share a model-driven color: muted blue-gray when no prediction is available, teal for lower scores, amber for intermediate scores, and red for higher scores. UI bands are illustrative presentation thresholds, not validated clinical cutoffs. Vessel panels summarize territory and show the predicted score when an inference has been returned.

The included geometry is a schematic rather than a licensed, anatomically validated patient mesh. The interior cross-section and plaque-like feature are illustrative only. A high-fidelity submission should replace this with an appropriately licensed 3D heart/coronary mesh and document the license, scale, orientation, and vessel-label correspondence.

## 5. Clinical dashboard and interpretability

The editable patient form is populated from the trained model's feature schema. The FastAPI service exposes health, schema, prediction, metrics, and global permutation-importance endpoints. For a prediction, the API provides an approximate one-feature-at-a-time perturbation relative to a median/mode reference. This is not SHAP/LIME, is not causal, and can miss feature interactions. Global permutation importance is descriptive. If a SHAP implementation is added, it must be computed against the fitted pipeline and described with its limitations.

## 6. Image-analysis pathway

A separate Kaggle notebook provides a starter 2D U-Net pipeline for coronary lumen segmentation from compatible ImageCAS/ImageCAS-X volumes and masks. It reports segmentation metrics such as Dice and IoU. These are not CAD prediction metrics. The public clinical table does not include patient-linked CT volumes or lesion masks, so the image model cannot be fused to clinical rows or claim patient-specific stenosis localization without verified linkage and suitable labels.

## 7. System integration and safety

The React/Vite client communicates with a FastAPI service. If model artifacts are absent, the interface should show model-not-trained status rather than fabricated predictions. Model scores are mapped to the corresponding vessel nodes but do not provide lesion coordinates. The interface must display this disclaimer prominently: **For educational/research decision support only; not a diagnosis or substitute for formal diagnostic imaging.** No real patient care use is intended.

## 8. Results and limitations

This code package intentionally contains no fabricated clinical results. The original dataset and CT volumes were unavailable in the packaged execution environment, so no real clinical training run or image-segmentation result is claimed. After training, replace this section with the notebook's actual per-target holdout metrics, model selection details, class counts, and any failures. Include the exact dataset citation and note the random seed and split. The dashboard concept artwork is a design mockup, not a live application capture. The present 3D anatomy is schematic; image segmentation is a separate starter; local perturbation is approximate; the sample is small; and there is no external clinical validation.

## References

1. Alizadehsani, R., Roshanzamir, M., & Sani, Z. (2013). *Extension of Z-Alizadeh Sani dataset*. UCI Machine Learning Repository. https://doi.org/10.24432/C5461K.
2. UCI Machine Learning Repository, dataset 411: https://archive.ics.uci.edu/dataset/411/extention%2Bof%2Bz%2Balizadeh%2Bsani%2Bdataset.
