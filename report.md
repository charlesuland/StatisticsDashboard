# StatisticsDashboard — Project Report

## Project description

StatisticsDashboard is a full-stack web application for exploratory model building and lightweight machine learning evaluation on user-supplied tabular data (CSV/XLSX). The app provides a Vue 3 + Vite frontend (`my-frontend/`) for dataset upload and configuration, and a FastAPI backend (`backend/`) that ingests uploaded files, runs preprocessing, trains multiple ML models, computes evaluation artifacts (ROC/PR curves, confusion matrices, learning curves, feature importances, and optional SHAP summaries), and stores server-rendered PNG plots in a SQLite database.

The primary goals are: fast iteration over different model classes, consistent preprocessing, and a small, easy-to-run dev environment for teaching and experimentation.

## Functions implemented

- File ingestion and preprocessing
	- Endpoint: `POST /dashboard/addDataSet` — accepts `.csv`, `.txt` (delimited), and `.xlsx` uploads. Files are sanitized, rows with missing values are dropped, and a processed CSV is written to `uploads/<username>/<filename>_processed.csv`. A JSON pipeline config is saved to `configs/<username>/<filename>_config.json`.

- Dataset metadata and column listing
	- `GET /dashboard/datasets` — lists datasets for the authenticated user.
	- `GET /dashboard/datasets/columns?filename=<name>` — returns column names of the processed CSV.

- Model evaluation
	- `POST /dashboard/modelevaluation` — trains a selected model from the registry (e.g., `logistic_regression`, `random_forest`, `svm`, `neural_net`) on the selected features and target using a specified test split. Returns scalar metrics and evaluation artifacts. Server renders and saves PNG plots (ROC, PR, confusion matrix, learning curve, feature importance, SHAP summary) to the `plots` table.

- Authentication and user management
	- JWT-based auth implemented in `backend/auth.py` and `backend/auth_routes.py` with registration and token issuance. `get_current_user` is used to protect dataset and model endpoints.

- Persistence
	- SQLAlchemy models in `backend/models.py` manage users, datasets, model metadata (per-model tables), and plots (binary PNG blobs).

## Technical details

- Database and server
	- SQLite via SQLAlchemy (file `app.db` created in `backend/` on startup). No migration tooling included; the app calls `Base.metadata.create_all(bind=engine)` in `backend/main.py`.
	- FastAPI backend.

- Languages and frameworks
	- Backend: Python 3.x, FastAPI, SQLAlchemy, pandas, scikit-learn, matplotlib, shap (optional).
	- Frontend: JavaScript (ES Modules), Vue 3, Vite, axios, vue-router.

- Dependency management and scripts
	- Python requirements: `backend/requirements.txt` (fastapi, uvicorn, python-multipart, sqlalchemy, python-jose, shap, sklearn, matplotlib).
	- Frontend scripts in `my-frontend/package.json`: `npm run dev` (Vite dev server), `npm run build`.

- File layout (key files)
	- `backend/main.py` — app startup, CORS config, router includes.
	- `backend/routes.py` — upload, dataset, and modelevaluation endpoints.
	- `backend/auth_routes.py` — auth endpoints and token helper.
	- `backend/models.py` — SQLAlchemy models (users, datasets, per-model metadata, plots).
	- `backend/ml/ModelManager.py` — centralized sanitization and evaluation helpers used by concrete managers in `backend/ml/*.py`.
	- `my-frontend/` — Vue components, views that call the backend endpoints.

## Architecture diagram (conceptual)

Client (Vue Vite dev server) <--> FastAPI (backend/routes.py) <--> ML managers (backend/ml/*)
																							|
																							+--> SQLite (SQLAlchemy models) stores users, datasets, model metadata, plots

Key data flows:
- Upload flow: Client -> POST /dashboard/addDataSet -> backend writes processed CSV to `uploads/<user>/` and a config to `configs/<user>/` -> create Dataset row in DB.
- Model eval flow: Client -> POST /dashboard/modelevaluation -> backend loads processed CSV -> instantiate manager from `ml.models[model]` -> manager.sanitize + train -> evaluate artifacts -> server-render plots -> save to DB.

## Highlighted features

- Centralized ML manager pattern
	- `ModelManager` provides robust `sanitize` logic that normalizes datatypes, coerces datetimes, converts object columns to numeric or categorical codes, fills numeric NaNs with column means, and converts datetimes to epoch seconds. This enforces consistent preprocessing across all model types.

- Model registry
	- Managers are registered in `backend/ml/__init__.py`'s `models` dict and referenced directly by name from `routes.py`. This makes adding a new model a focused change: implement manager + add registry key.

- Server-side rendering and storage of plots
	- The backend generates evaluation plots with matplotlib and stores PNG bytes in the `plots` table so they can be returned or referenced later without re-running computations.

- Lightweight dev setup
	- Minimal dependencies and no heavyweight orchestration: SQLite + single Python process + Vite dev server. Good for teaching and reproducibility.

## Discussion — methods comparison, trade-offs, and limitations (expanded)

This section provides an evidence-focused comparison of model families implemented in the repository, practical guidance for reproducible experiments, and prioritized, actionable changes.

Summary of model families and when to prefer them
- Tree ensembles (Random Forest, Gradient/Boosting, Bagging)
  - Strengths: handle mixed datatypes and missing-value imputation well after simple preprocessing; provide fast, reliable feature-importance estimates; often high out-of-the-box accuracy on tabular data.
  - Weaknesses: larger memory and CPU usage for large forests; interpretation beyond global importances can require SHAP or surrogate models.
  - When to use here: default first-line models for heterogeneous features and baseline comparisons.

- Linear models (Logistic / Linear Regression)
  - Strengths: fast, interpretable coefficients, low variance; useful as a baseline and for feature selection.
  - Weaknesses: underfit when relationships are non-linear or when interactions are important.
  - When to use: quick baselines and datasets where interpretability matters.

- Support Vector Machines (SVM)
  - Strengths: effective in medium-dimensional problems; kernel methods capture non-linear decision boundaries.
  - Weaknesses: require feature scaling; training time and memory scale poorly with sample size (especially with non-linear kernels).
  - When to use: smaller datasets or when margin-based classifiers are preferred, with a StandardScaler in the preprocessing pipeline.

- Neural networks (basic DNN manager)
  - Strengths: flexible function approximators, can model complex interactions.
  - Weaknesses: sensitive to input scaling, hyperparameters, and require more careful training; risk of overfitting on small datasets.
  - When to use: larger labeled datasets and when you can afford tuning; in the future, replace scikit-learn wrapper with frameworks (PyTorch/TF).

Practical suggestions for improving reproducibility and pedagogy
- Add a reproducible experiment notebook that:
  1. Uploads a small sample dataset to the backend.
  2. Runs the three canonical models with fixed seeds.
  3. Collects plots and metrics and shows step-by-step how to interpret them (ROC vs PR, calibration).
- Add small unit tests under `tests/` that construct tiny DataFrames and call each manager's train/predict methods to catch regressions. Example tests already suggested under `tests/test_ml_models.py`.

Prioritized future work (short roadmap)
1. Immediate (low friction)
   - Add StandardScaler option and integrate into SVM and neural-net managers.
   - Make SHAP sampling-based and configurable.
   - Move secrets to environment variables and sanitize filenames.
2. Medium term
   - Add Alembic for DB migrations and move DB config to env-based settings.
   - Introduce a simple job queue for long-running evaluations and SHAP computations.
   - Expose job status endpoints and enable asynchronous triggers from the frontend.
3. Longer term
   - Replace the experimental DNN manager with a lightweight PyTorch/TF backend for larger experiments.
   - Add CI to run unit tests for each manager on sample DataFrames and run linting.