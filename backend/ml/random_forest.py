from typing import Any
import pandas as pd
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    roc_curve,
    precision_recall_curve,
)
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split


class RandForestManager:
    def __init__(
        self,
        dataframe: pd.DataFrame,
        test_split,
        n_estimators: int = 100,
        max_depth: int | None = None,
        random_state: int = 42,
        classifier: bool = False,
    ):
        self.df = dataframe
        self.test_split = test_split / 100
        self.n_estimators = n_estimators
        self.max_depth = max_depth
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
            model = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
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
                # top-level classifier metrics
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
            model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=self.random_state,
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            return {
                "r2": float(r2_score(y_test, y_pred)),
                "mse": float(mean_squared_error(y_test, y_pred)),
                "mae": float(mean_absolute_error(y_test, y_pred)),
            }
