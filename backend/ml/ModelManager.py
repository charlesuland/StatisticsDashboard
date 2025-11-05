from abc import ABCMeta, abstractmethod
from typing import Any, Optional

import numpy as np
import pandas as pd
import pandas.api.types as ptypes
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import learning_curve
from sklearn.preprocessing import StandardScaler

try:
    import shap  # optional
except Exception:
    shap = None


class ModelManager(metaclass=ABCMeta):
    def __init__(self, dataframe: pd.DataFrame, test_split: int):
        # store a raw copy of the dataframe; per-model training will sanitize features
        # and handle the target column explicitly via prepare_xy
        self.df = dataframe.copy()
        self.test_split = test_split / 100

    @abstractmethod
    def train(self, target, features, *args, **kwargs) -> dict[str, Any]:
        pass

    def sanitize(
        self, df: Optional[pd.DataFrame] = None, drop_threshold: float = 0.5
    ) -> pd.DataFrame:
        if df is None:
            # if called before self.df exists, just return an empty DataFrame defensive
            df = getattr(self, "df", pd.DataFrame())
        df = df.copy()

        # Drop duplicate rows
        df = df.drop_duplicates().reset_index(drop=True)

        # Drop columns with too many missing values
        if len(df) > 0:
            thresh = int((1.0 - drop_threshold) * len(df))
            if thresh <= 0:
                thresh = 1
            df = df.dropna(axis=1, thresh=thresh)

        # Process object columns: try datetime -> numeric -> categorical codes
        obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
        for col in obj_cols:
            series = df[col]
            # try parse datetime (prefer datetimes only if a reasonable fraction parse)
            try:
                parsed = pd.to_datetime(series, errors="coerce")
                if parsed.notna().sum() >= max(1, int(0.5 * len(df))):
                    df[col] = parsed
                    continue
            except Exception:
                pass

            # try numeric coercion
            coerced = pd.to_numeric(series, errors="coerce")
            if coerced.notna().sum() > 0:
                df[col] = coerced
            else:
                # fallback to categorical codes (ensure integer dtype)
                codes = pd.Categorical(series).codes
                # convert codes (which may be -1 for NaN) to int64
                df[col] = pd.Series(codes, index=df.index, dtype="int64")

        # Ensure datetime columns are native numpy datetime64[ns]
        for col in df.columns:
            # normalize any datetime-like columns to pandas datetime
            if ptypes.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_datetime(df[col], errors="coerce", utc=False)

        # Convert datetime columns to numeric epoch seconds to avoid dtype mixing
        datetime_cols = [c for c in df.columns if ptypes.is_datetime64_any_dtype(df[c])]
        for c in datetime_cols:
            # astype('int64') gives ns since epoch; convert to seconds as float64
            try:
                df[c] = df[c].astype("int64") / 1e9
            except Exception:
                # fallback: coerce then convert
                df[c] = pd.to_datetime(df[c], errors="coerce").astype("int64") / 1e9
            # ensure float dtype
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")

        # Normalize numeric dtypes to float64 to avoid nullable-int / float promotion issues
        num_cols = [c for c in df.columns if ptypes.is_numeric_dtype(df[c])]
        if num_cols:
            df[num_cols] = (
                df[num_cols].apply(pd.to_numeric, errors="coerce").astype("float64")
            )

        # Fill numeric NaNs with column mean (after conversion to float64)
        for col in num_cols:
            if df[col].isna().any():
                try:
                    mean_val = float(df[col].mean(skipna=True))
                except Exception:
                    mean_val = 0.0
                df[col] = df[col].fillna(mean_val)

        # Reset index and return
        df = df.reset_index(drop=True)
        return df

    def prepare_xy(self, features: list[str], target: str, classifier: bool | None = None):
        """
        Prepare X (features) and y (target) for training.

        - Sanitizes only the feature columns using `sanitize` so we don't accidentally
          convert or re-encode the target column in a way that breaks stratify or
          label semantics.
        - Handles target encoding: for classification (classifier=True) or when the
          target is non-numeric, convert to categorical integer codes. For
          regression (classifier=False) coerce target to float and fill NaNs with
          the column mean.

        Returns (X, y) where X is a 2D numpy-compatible array / DataFrame and y is a
        1-D pandas Series (numeric dtypes).
        """
        if target not in self.df.columns:
            raise ValueError(f"Target column '{target}' not found in dataframe")

        # Work on copies
        X_df = self.df[features].copy()
        y_s = self.df[target].copy()

        # Sanitize only the feature frame (this will coerce datetimes/numerics/categoricals)
        X_df = self.sanitize(X_df)
        y_s = y_s.loc[X_df.index]
        # Decide how to treat target
        # If classifier flag not provided, infer from dtype: object or categorical -> classifier
        if classifier is None:
            inferred_classifier = not (ptypes.is_float_dtype(y_s) or ptypes.is_integer_dtype(y_s))
        else:
            inferred_classifier = bool(classifier)

        # If a truth_spec is provided on the manager, apply it to coerce target to binary
        truth_spec = getattr(self, 'truth_spec', None)
        if inferred_classifier and truth_spec:
            try:
                op = truth_spec.get('operator')
                val = truth_spec.get('value')
                # Decide whether to parse value as number
                parsed_val = None
                try:
                    parsed_val = float(val)
                except Exception:
                    parsed_val = val

                # Build boolean mask according to operator
                if op in ('==', '!='):
                    if op == '==':
                        mask = y_s == parsed_val
                    else:
                        mask = y_s != parsed_val
                else:
                    # comparison operators: ensure numeric comparison
                    y_num = pd.to_numeric(y_s, errors='coerce')
                    if pd.isna(parsed_val):
                        # cannot compare numeric if parsed_val not numeric; fallback to equality
                        mask = y_s == parsed_val
                    else:
                        if op == '>':
                            mask = y_num > parsed_val
                        elif op == '>=':
                            mask = y_num >= parsed_val
                        elif op == '<':
                            mask = y_num < parsed_val
                        elif op == '<=':
                            mask = y_num <= parsed_val
                        else:
                            mask = y_s == parsed_val

                # Map to integer 0/1, treat NaN as False (0)
                y_s = pd.Series(mask.astype('int').fillna(0).astype('int64'), index=y_s.index)
                # After coercion, treat as classifier with two classes
                inferred_classifier = True
            except Exception as e:
                # If truth spec fails, log and continue with regular inference
                print('Warning: failed to apply truth_spec:', e)

        # Handle classification targets: map to integer codes if necessary
        if inferred_classifier:
            # If it's numeric already but continuous, we still coerce to categorical
            if not ptypes.is_integer_dtype(y_s):
                # try numeric coercion first: if many values parse, keep numeric
                coerced = pd.to_numeric(y_s, errors="coerce")
                if coerced.notna().sum() >= max(1, int(0.5 * len(y_s))):
                    # treat as numeric labels but cast to integer if it's integral
                    if np.all(np.mod(coerced.dropna(), 1) == 0):
                        y_s = coerced.fillna(coerced.mean()).astype("int64")
                    else:
                        # numeric but non-integer: keep as float
                        y_s = coerced.fillna(coerced.mean()).astype("float64")
                else:
                    # convert to categorical codes
                    cats = pd.Categorical(y_s)
                    y_s = pd.Series(cats.codes, index=y_s.index, dtype="int64")
        else:
            # Regression target: coerce to numeric float and fill NaNs with mean
            y_num = pd.to_numeric(y_s, errors="coerce")
            if y_num.isna().any():
                try:
                    mean_val = float(y_num.mean(skipna=True))
                except Exception:
                    mean_val = 0.0
                y_num = y_num.fillna(mean_val)
            y_s = y_num.astype("float64")

        # Ensure X and y indices align and return
        X_df = X_df.reset_index(drop=True)
        # --- Feature scaling: scale numeric features for all models ---
        try:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_df.values)
            # reconstruct DataFrame to keep column names
            X_df = pd.DataFrame(X_scaled, columns=X_df.columns, index=X_df.index)
            # replace any inf/nan introduced by zero-variance columns
            X_df = X_df.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        except Exception as e:
            # if scaling fails, fall back to unscaled features but do not crash
            print("Feature scaling failed, proceeding with unscaled features:", e)
        y_s = y_s.reset_index(drop=True)
        return X_df, y_s

    def evaluate_model(
    self,
    model,
    X_train,
    X_test,
    y_train,
    y_test,
    is_classifier: bool = True,
    feature_names: list | None = None,
) -> dict[str, Any]:
        """
        Evaluate a trained model and return metrics, learning curves, and optional SHAP values.

        Handles:
        - Confusion matrix (classification)
        - ROC / PR curves and AUC (binary & multi-class)
        - Feature importances / coefficients
        - Learning curve
        - SHAP summary (optional)
        """
        out: dict[str, Any] = {}

        # --------------------------
        # Confusion Matrix (Classifiers)
        # --------------------------
        if is_classifier:
            try:
                y_pred = model.predict(X_test)
                out["confusion_matrix"] = confusion_matrix(y_test, y_pred).tolist()
            except Exception as e:
                print("Confusion matrix failed:", e)

        # --------------------------
        # ROC / PR / AUC
        # --------------------------
        if is_classifier:
            y_proba = None
            try:
                if hasattr(model, "predict_proba"):
                    y_proba = model.predict_proba(X_test)
                elif hasattr(model, "decision_function"):
                    df = model.decision_function(X_test)
                    if df.ndim == 1:
                        # Binary decision function → scale to 0-1
                        from sklearn.preprocessing import MinMaxScaler

                        scaler = MinMaxScaler()
                        y_proba = scaler.fit_transform(df.reshape(-1, 1))
                    else:
                        y_proba = df  # multi-class decision function

                if y_proba is not None:
                    from sklearn.preprocessing import label_binarize
                    from sklearn.metrics import (
                        average_precision_score,
                        precision_recall_curve,
                        roc_auc_score,
                        roc_curve,
                    )

                    classes = np.unique(y_test)

                    if len(classes) == 2:
                        # Binary classification
                        scores = y_proba[:, 1] if y_proba.ndim == 2 else y_proba.ravel()
                        fpr, tpr, _ = roc_curve(y_test, scores)
                        prec, rec, _ = precision_recall_curve(y_test, scores)
                        out["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}
                        out["pr_curve"] = {"precision": prec.tolist(), "recall": rec.tolist()}
                        out["roc_auc"] = float(roc_auc_score(y_test, scores))
                        out["pr_auc"] = float(average_precision_score(y_test, scores))
                    else:
                        # Multi-class classification
                        y_true_bin = label_binarize(y_test, classes=classes)
                        # ROC AUC (One-vs-Rest)
                        try:
                            out["roc_auc"] = float(
                                roc_auc_score(y_true_bin, y_proba, average="macro", multi_class="ovr")
                            )
                        except Exception as e:
                            print("Multi-class ROC AUC failed:", e)
                            out["roc_auc"] = None
                        # Average Precision (macro)
                        try:
                            out["pr_auc"] = float(
                                average_precision_score(y_true_bin, y_proba, average="macro")
                            )
                        except Exception as e:
                            print("Multi-class PR AUC failed:", e)
                            out["pr_auc"] = None

            except Exception as e:
                print("ROC/PR computation failed:", e)

        # --------------------------
        # Feature Importance / Coefficients
        # --------------------------
        try:
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
                names = feature_names or [f"f{i}" for i in range(len(importances))]
                out["feature_importance"] = [
                    {"name": n, "importance": float(v)} for n, v in zip(names, importances)
                ]
            elif hasattr(model, "coef_"):
                coef = model.coef_
                if coef.ndim == 1:
                    names = feature_names or [f"f{i}" for i in range(len(coef))]
                    out["feature_importance"] = [
                        {"name": n, "importance": float(abs(v))} for n, v in zip(names, coef)
                    ]
                else:
                    # multiclass: sum abs across classes
                    agg = np.sum(np.abs(coef), axis=0)
                    names = feature_names or [f"f{i}" for i in range(len(agg))]
                    out["feature_importance"] = [
                        {"name": n, "importance": float(v)} for n, v in zip(names, agg)
                    ]
        except Exception as e:
            print("Feature importance extraction failed:", e)

        # --------------------------
        # Learning Curve
        # --------------------------
        try:
            lc_res = learning_curve(
                model,
                np.vstack([X_train, X_test]),
                np.concatenate([y_train, y_test]),
                train_sizes=np.linspace(0.1, 1.0, 5),
                cv=3,
                scoring=None,
                n_jobs=1,
                shuffle=True,
                random_state=42,
                return_times=False,
            )
            # learning_curve may return extra timing arrays; only take the first three
            train_sizes, train_scores, test_scores = lc_res[:3]
            out["learning_curve"] = {
                "train_sizes": train_sizes.tolist(),
                "train_scores_mean": np.mean(train_scores, axis=1).tolist(),
                "test_scores_mean": np.mean(test_scores, axis=1).tolist(),
            }
        except Exception as e:
            print("Learning curve computation failed:", e)

        # --------------------------
        # SHAP summary (optional)
        # --------------------------
        if shap is not None:
            try:
                explainer = None
                if hasattr(shap, "TreeExplainer") and hasattr(model, "feature_importances_"):
                    explainer = shap.TreeExplainer(model)
                else:
                    explainer = shap.Explainer(model, X_train)
                sv = explainer(X_test)
                mean_abs = np.mean(np.abs(sv.values), axis=0)
                names = feature_names or [f"f{i}" for i in range(len(mean_abs))]
                out["shap_summary"] = [
                    {"name": n, "mean_abs_shap": float(v)} for n, v in zip(names, mean_abs)
                ]
            except Exception as e:
                print("SHAP computation failed:", e)

        return out
