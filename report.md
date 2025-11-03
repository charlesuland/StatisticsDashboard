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

## Discussion — methods comparison, trade-offs, and limitations

This app implements several model classes (logistic regression, linear regression, decision trees, bagging, boosting, random forest, SVM, and a basic neural net manager). Below I compare approaches and connect them to the repository's design choices.

1) Tree ensembles (Random Forest, Bagging, Boosting)
	 - Strengths: handle mixed datatypes, robust to outliers, provide feature importances via `feature_importances`, often strong off-the-shelf performance, less need for scaling or heavy preprocessing.
	 - In this repo: `RandForestManager` and `BaggingManager` benefit from the `ModelManager.sanitize` (especially handling categorical codes and datetime conversion), and SHAP's `TreeExplainer` can be used to produce SHAP summaries quickly.
	 - Trade-offs: ensembles are heavier computationally and can be memory intensive for large datasets. The current learning-curve computation (learning_curve with cv=3) can be expensive; the code runs with n_jobs=1 to limit parallelism.

2) Support Vector Machines (SVM)
	 - Strengths: effective in high-dimensional spaces, robust regularization, can work well for small-to-medium datasets.
	 - Trade-offs: SVMs require feature scaling and are slower for large datasets (kernel methods scale poorly). Implementation in `support_vector_machine.py` must ensure numeric features are scaled beforehand — currently `ModelManager` does not scale features, so dividing responsibilities (preprocessing vs model pipeline) should be considered.

3) Neural Networks (DNN)
	 - Strengths: highly expressive; can learn complex interactions and representation learning from raw features.
	 - Trade-offs: require careful hyperparameter tuning, more training time, and are sensitive to input scaling and missing-value strategies. The repo's `neural_net` manager wraps a simple DNN; for production or larger experiments, one would integrate PyTorch or TensorFlow-based training loops with GPU support — the current CPU-only, scikit-learn-like approach is fine for demos.

4) Linear/Logistic regression
	 - Strengths: interpretable coefficients, fast training, small memory footprint.
	 - Trade-offs: less expressive; may underperform when relationships are non-linear. Still valuable as baselines.

Evidence-based comparison (how to reproduce locally)
- Run repeated experiments on a small uploaded dataset and compare metrics returned by `/dashboard/modelevaluation` (e.g., `roc_auc`, `pr_auc`, `accuracy`). The managers already return cross-validation summaries (`cv_mean` and `cv_std`) for classifiers — use these fields to compare stability across models.

Limitations & current gaps
- No scaling pipeline: `ModelManager.sanitize` normalizes types and imputes means, but it does not apply feature scaling (StandardScaler/MinMax) which is important for SVMs and neural nets.
- No migrations: schema changes will recreate models with `create_all` and may not be safe for production data—Alembic is recommended for future work.
- Single-process evaluation: CPU-bound training and evaluation (especially SHAP) can be slow; there is no job queue or async task processing. For larger runs, integrate a background worker (Celery/RQ) or async tasks.
- Security: `SECRET_KEY` is hard-coded in `backend/auth.py` and should be moved to environment variables. Uploaded file handling should validate filenames and sanitize paths; current code uses `os.path.join` with username but doesn't fully validate filename content.

Future work
- Add a minimal pipeline abstraction that composes `ModelManager.sanitize` + optional scalers + model pipeline (e.g., scikit-learn Pipelines). This will standardize preprocessing for SVMs and DNNs.
- Integrate Alembic for DB migrations and move DB credentials to configuration/env variables.
- Add a background task queue for long-running evaluations and SHAP computations, and provide job status endpoints.
- Add automated unit tests for each ML manager (small DataFrame smoke tests) and expand CI to run them.