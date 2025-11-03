# Model Manager Options

## All
`dataframe` - pandas.DataFrame containing the dataset.  
`test_split` - percentage (e.g. 20) representing the test set size. 20 == 20%
`classifier` (where available) - boolean. If true, uses classifier model
`random_state` (default: 42) - rng state for reproducability

General I/O contract:
- Regressors return: `{"r2_score": float, "mse": float, "mae": float}`
- Classifiers return: `{"accuracy": float, "precision": float, "recall": float, "f1": float}`
  - If needed, they also return (in the same dictionary): `{"roc_auc": float, "pr_auc": float, "roc_curve": {"fpr": [...], "tpr": [...]}, "pr_curve": {"precision": [...], "recall": [...]}}`
  - 
- All managers expose `train(target, features)` which: splits data using `test_split`, fits the estimator, predicts on the test set, and returns metrics.

**TODO**
cross-validation

---

## Linear Regression - LinRegManager
 - `fit_intercept`: bool (default: True) - whether to calculate the intercept for the model.
---

## Logistic Regression - LogRegManager
**Classification ONLY**
- `penalty`: str (default: "l2") - regularization penalty.
- `C`: float (default: 1.0) - inverse regularization strength.
- `solver`: str (default: "lbfgs") - optimization algorithm.
- `max_iter`: int (default: 1000) - max solver iterations.

---

## Decision Tree - DecisionTreeManager
- `max_depth`: int | None (default: None) - max tree depth.
- `min_samples_split`: int (default: 2) - min samples to split a node.
- `random_state`: int (default: 42) - reproducibility.
- `classifier`: bool (default: False) - if True, uses DecisionTreeClassifier.

---

## Random Forest - RandForestManager
- `n_estimators`: int (default: 100) - number of trees.
- `max_depth`: int | None (default: None) - max depth per tree.
- `random_state`: int (default: 42)
- `classifier`: bool (default: False) - uses RandomForestClassifier if True.

---

## Bagging - BaggingManager
- `n_estimators`: int (default: 10)
- `max_samples`: float | int (default: 1.0)
- `random_state`: int (default: 42)
- `classifier`: bool (default: False)

---

# Boosting - BoostingManager
  - `n_estimators`: int (default: 50)
  - `learning_rate`: float (default: 1.0)
  - `random_state`: int (default: 42)
  - `classifier`: bool (default: False)

---

## Neural Network - NeuralNetManager
- `hidden_layer_sizes`: sequence (default: [100]) - architecture tuple/list.
- `activation`: str (default: "relu")
- `solver`: str (default: "adam")
- `lr`: float (default: 0.001)
- `max_iter`: int (default: 500)
- `random_state`: int (default: 42)
- `classifier`: bool (default: False) - uses MLPClassifier if True.

---

## Support Vector Machine - SVMManager
- `kernel`: str (default: "rbf") - kernel type.
- `C`: float (default: 1.0) - regularization.
- `gamma`: str | float (default: "scale") - kernel coefficient.
- `random_state`: int (default: 42)
- `classifier`: bool (default: False) - uses SVC if True, otherwise SVR.

---

# User-defined DNN - UserDefinedDNNManager
- `hidden_layer_sizes`: Iterable[int] (default: [100]) - user architecture.
- `activation`: `Literal["relu", "identity", "logistic", "tanh"]` -  default `"relu"`
- `solver`: `Literal["lbfgs", "sgd", "adam"]` - default `"adam"`
- `learning_rate_init`: float
- `max_iter`: float
- `random_state`: float
- `classifier`: bool (default: False) - uses MLPClassifier if True.

---

# Return values for manager.train(target, features)

All managers return a JSON-serializable dict with model metrics and optional artifacts.

- Common keys (present where applicable)
  - For regressors:
    - r2: float
    - mse: float
    - mae: float
  - For classifiers:
    - accuracy: float
    - precision: float
    - recall: float
    - f1: float
    - roc_auc: float (when probabilities available)
    - pr_auc: float (when probabilities available)
  - Cross-validation summaries (optional)
    - cv_mean: dict — e.g. {"accuracy_mean": 0.91, "precision_mean": 0.89} or {"r2_mean": 0.72, "mse_mean": 1.23}
    - cv_std: dict — same keys as cv_mean with std values
  - Evaluation artifacts (optional)
    - roc_curve: {"fpr": [...], "tpr": [...]} — arrays of floats
    - pr_curve: {"precision": [...], "recall": [...]} — arrays of floats
    - confusion_matrix: [[int,...], [...,...]] — 2D list of integers
    - feature_importance: [{"name": str, "importance": float}, ...]
    - learning_curve: {"train_sizes": [...], "train_scores_mean": [...], "test_scores_mean": [...]}
    - shap_summary: [{"name": str, "mean_abs_shap": float}, ...]

Notes
- Keys not applicable or unavailable (e.g., roc_auc when no probabilities) are omitted.
- Numeric values are plain Python floats (JSON numbers); arrays are lists.
- cv_mean/cv_std keys follow the metric names used by sklearn cross_validate with `_mean`/`_std` suffixes.

Examples (minimal)
- Classifier (binary):
  {
    "accuracy": 0.92,
    "precision": 0.91,
    "recall": 0.90,
    "f1": 0.905,
    "roc_auc": 0.96,
    "roc_curve": {"fpr": [0.0, 0.1, ...], "tpr": [0.0, 0.85, ...]},
    "confusion_matrix": [[50, 5], [4, 41]],
    "feature_importance": [{"name":"x1","importance":0.34}, {"name":"x2","importance":0.12}],
    "learning_curve": {"train_sizes":[20,40,80],"train_scores_mean":[0.9,0.92,0.95],"test_scores_mean":[0.85,0.88,0.9]},
    "cv_mean": {"accuracy_mean":0.91, "f1_mean":0.90},
    "cv_std": {"accuracy_std":0.02, "f1_std":0.015}
  }

- Regressor:
  {
    "r2": 0.78,
    "mse": 1.23,
    "mae": 0.87,
    "feature_importance": [{"name":"x1","importance":0.45}, ...],
    "learning_curve": {...},
    "cv_mean": {"r2_mean":0.75, "mse_mean":1.34},
    "cv_std": {"r2_std":0.03, "mse_std":0.12}
  }
