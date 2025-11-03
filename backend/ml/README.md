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