from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import BaggingClassifier, BaggingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, roc_curve, precision_recall_curve
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold, cross_validate

from . import ModelManager

class BaggingManager(ModelManager):
    def __init__(self, dataframe: pd.DataFrame, test_split, n_estimators: int = 10, max_samples: float | int = 1.0, random_state: int = 42, classifier: bool = False, cv_folds: int = 5):
        super().__init__(dataframe, test_split)
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.random_state = random_state
        self.classifier = classifier
        self.cv_folds = cv_folds

    def train(self, target, features):
        X, y = self.prepare_xy(features, target, classifier=self.classifier)

        # Cross-validation summary
        if self.classifier:
            scoring = {"accuracy": "accuracy", "precision": "precision_macro", "recall": "recall_macro", "f1": "f1_macro", "roc_auc": "roc_auc", "pr_auc": "average_precision"}
            cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
            try:
                cv_res = cross_validate(BaggingClassifier(n_estimators=self.n_estimators, max_samples=self.max_samples, random_state=self.random_state), X, y, cv=cv, scoring=scoring)
                cv_mean = {k + "_mean": float(np.mean(cv_res[f"test_{k}"])) for k in scoring}
                cv_std = {k + "_std": float(np.std(cv_res[f"test_{k}"])) for k in scoring}
            except Exception:
                cv_mean = {}
                cv_std = {}
        else:
            scoring = {"r2": "r2", "neg_mse": "neg_mean_squared_error", "neg_mae": "neg_mean_absolute_error"}
            cv = KFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
            try:
                cv_res = cross_validate(BaggingRegressor(n_estimators=self.n_estimators, max_samples=self.max_samples, random_state=self.random_state), X, y, cv=cv, scoring=scoring)
                cv_mean = {"r2_mean": float(np.mean(cv_res["test_r2"])), "mse_mean": float(-np.mean(cv_res["test_neg_mse"])), "mae_mean": float(-np.mean(cv_res["test_neg_mae"]))}
                cv_std = {"r2_std": float(np.std(cv_res["test_r2"])), "mse_std": float(np.std(cv_res["test_neg_mse"])), "mae_std": float(np.std(cv_res["test_neg_mae"]))}
            except Exception:
                cv_mean = {}
                cv_std = {}

        # Hold-out split for final training/evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.test_split,
            random_state=self.random_state,
            stratify=y if self.classifier else None,
        )

        if self.classifier:
            model = BaggingClassifier(
                n_estimators=self.n_estimators,
                max_samples=self.max_samples,
                random_state=self.random_state,
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = None
            try:
                y_proba = model.predict_proba(X_test)[:, 1]
            except Exception:
                y_proba = None

            result: dict[str, Any] = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, average="macro")),
                "recall": float(recall_score(y_test, y_pred, average="macro")),
                "f1": float(f1_score(y_test, y_pred, average="macro")),
            }
            if y_proba is not None:
                result["roc_auc"] = float(roc_auc_score(y_test, y_proba))
                result["pr_auc"] = float(average_precision_score(y_test, y_proba))
                fpr, tpr, _ = roc_curve(y_test, y_proba)
                precision, recall, _ = precision_recall_curve(y_test, y_proba)
                result["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}
                result["pr_curve"] = {
                    "precision": precision.tolist(),
                    "recall": recall.tolist(),
                }
            result["cv_mean"] = cv_mean
            result["cv_std"] = cv_std
            try:
                eval_artifacts = self.evaluate_model(
                    model,
                    X_train,
                    X_test,
                    y_train,
                    y_test,
                    is_classifier=True,
                    feature_names=features,
                )
                result.update(eval_artifacts)
            except Exception:
                pass
            return result
        else:
            model = BaggingRegressor(
                n_estimators=self.n_estimators,
                max_samples=self.max_samples,
                random_state=self.random_state,
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            result: dict[str, Any] = {
                "r2": float(r2_score(y_test, y_pred)),
                "mse": float(mean_squared_error(y_test, y_pred)),
                "mae": float(mean_absolute_error(y_test, y_pred)),
            }
            result["cv_mean"] = cv_mean
            result["cv_std"] = cv_std
            try:
                eval_artifacts = self.evaluate_model(
                    model,
                    X_train,
                    X_test,
                    y_train,
                    y_test,
                    is_classifier=False,
                    feature_names=features,
                )
                result.update(eval_artifacts)
            except Exception:
                pass
            return result
