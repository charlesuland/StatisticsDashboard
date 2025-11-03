from typing import Any, Literal
import numpy as np
import pandas as pd
from sklearn.calibration import label_binarize
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.multiclass import OneVsRestClassifier

from . import ModelManager


class LogRegManager(ModelManager):
    def __init__(
        self,
        dataframe: pd.DataFrame,
        test_split,
        penalty: Literal["l1", "l2", "elasticnet"] = "l2",
        C: float = 1.0,
        solver: Literal[
            "lbfgs", "liblinear", "newton-cg", "newton-cholesky", "sag", "saga"
        ] = "lbfgs",
        max_iter: int = 1000,
        cv_folds: int = 5,
    ):
        super().__init__(dataframe, test_split)
        self.penalty = penalty
        self.C = C
        self.solver = solver
        self.max_iter = max_iter
        self.cv_folds = cv_folds

    def train(self, target, features):
        # prepare features and target; logistic regression is a classifier
        X, y = self.prepare_xy(features, target, classifier=True)
        counts = y.value_counts()
        valid_classes = counts[counts >= 2].index
        mask = y.isin(valid_classes)

        X_filtered = X.loc[mask]
        y_filtered = y.loc[mask]
        X=X_filtered
        y = y_filtered
        # Cross-validation summary (classification)
        scoring = {
            "accuracy": "accuracy",
            "precision": "precision_macro",
            "recall": "recall_macro",
            "f1": "f1_macro",
            "roc_auc": "roc_auc",
            "pr_auc": "average_precision",
        }
        cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=42)
        try:
            cv_res = cross_validate(
                LogisticRegression(
                    penalty=self.penalty,
                    C=self.C,
                    solver=self.solver,
                    max_iter=self.max_iter,
                ),
                X,
                y,
                cv=cv,
                scoring=scoring,
            )
            cv_mean = {k + "_mean": float(np.mean(cv_res[f"test_{k}"])) for k in scoring}
            cv_std = {k + "_std": float(np.std(cv_res[f"test_{k}"])) for k in scoring}
        except Exception:
            cv_mean = {}
            cv_std = {}
        y = pd.Categorical(y).codes
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=42, stratify=y
        )
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        X_train = X_train_scaled
        X_test = X_test_scaled
        model = OneVsRestClassifier(
            LogisticRegression(
            penalty=self.penalty,
            C=1,
            solver=self.solver,
            max_iter=self.max_iter,
            multi_class='ovr',
        ))

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = None
        try:
            y_proba = model.predict_proba(X_test)[:, 1]
        except Exception:
            y_proba = None

        result: dict[str, Any] = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, average="macro")),
            "f1": float(f1_score(y_test, y_pred, average="macro")),
        }
        if y_proba is not None:
            result["roc_auc"] = float(roc_auc_score(y_test, y_proba, multi_class='ovr', average="macro"))
            y_true_bin = label_binarize(y_test, classes=np.unique(y_test))
            average_precision_score(y_true_bin, y_proba, average="macro")
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
