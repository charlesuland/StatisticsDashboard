from typing import Any

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_curve,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from backend.ml import ModelManager


class DecisionTreeManager(ModelManager):
    def __init__(
        self,
        dataframe: pd.DataFrame,
        test_split,
        max_depth: int | None = None,
        min_samples_split: int = 2,
        random_state: int = 42,
        classifier: bool = False,
    ):
        self.df = self.sanitize(dataframe)
        self.test_split = test_split / 100
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.random_state = random_state
        self.classifier = classifier

    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.test_split,
            random_state=self.random_state,
            stratify=y if self.classifier else None,
        )

        if self.classifier:
            model = DecisionTreeClassifier(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
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
            return result
        else:
            model = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                random_state=self.random_state,
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            return {
                "r2": float(r2_score(y_test, y_pred)),
                "mse": float(mean_squared_error(y_test, y_pred)),
                "mae": float(mean_absolute_error(y_test, y_pred)),
            }
