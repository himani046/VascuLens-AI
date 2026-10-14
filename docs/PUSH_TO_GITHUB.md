# Working locally and pushing updates

This repository has a `vasculens-ai` branch containing the current implementation. Use the branch while reviewing changes before merging into `main`.

## Clone the project

```bash
git clone --branch vasculens-ai https://github.com/himani046/VascuLens-AI.git
cd VascuLens-AI
```

## Run backend

```bash
cd backend
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python train.py --data "/path/to/extention of Z-Alizadeh sani dataset.xlsx"
uvicorn app:app --reload --port 8000
```

The original clinical dataset is not included. Do not commit the patient dataset, serialized model artifacts, real patient identifiers, or secret keys. The training script writes local artifacts under `backend/artifacts/`.

## Run frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The frontend uses `VITE_API_URL=http://127.0.0.1:8000` by default. The API is available at `http://127.0.0.1:8000/docs`.

## Notebooks

Open the notebooks in `notebooks/` in Kaggle. Attach the original UCI dataset as a Kaggle input to the clinical notebooks. Attach ImageCAS/ImageCAS-X CCTA volumes and masks for the segmentation notebook. Follow each notebook's printed dataset checks before training.

## Push your own local changes

```bash
git checkout vasculens-ai
git add .
git commit -m "Describe your update"
git push origin vasculens-ai
```

## Validation notes

- Run tests from the backend folder with `python -m unittest discover -s tests -v`.
- The dashboard's anatomical scene is schematic, not an anatomy-grade mesh.
- Image segmentation metrics (Dice/IoU) are not CAD accuracy or stenosis-grade metrics.
- No clinical accuracy number is guaranteed. Report only results actually produced by the specified validation procedure.
- The system is for research/education only and is not a diagnostic tool.
