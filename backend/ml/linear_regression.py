from typing import Any
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, KFold, cross_validate

from . import ModelManager


class LinRegManager(ModelManager):
    def __init__(self, dataframe: pd.DataFrame, test_split, fit_intercept: bool = True, cv_folds: int = 5):
        self.df = self.sanitize(dataframe)
        self.test_split = test_split / 100
        self.fit_intercept = fit_intercept
        self.cv_folds = cv_folds

    # renamed to `train` to match abstract interface and use self.test_split
    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        # Cross-validation summary (regression)
        scoring = {"r2": "r2", "neg_mse": "neg_mean_squared_error", "neg_mae": "neg_mean_absolute_error"}
        cv = KFold(n_splits=self.cv_folds, shuffle=True, random_state=42)
        try:
            cv_res = cross_validate(LinearRegression(fit_intercept=self.fit_intercept), X, y, cv=cv, scoring=scoring)
            cv_mean = {"r2_mean": float(np.mean(cv_res["test_r2"])), "mse_mean": float(-np.mean(cv_res["test_neg_mse"])), "mae_mean": float(-np.mean(cv_res["test_neg_mae"]))}
            cv_std = {"r2_std": float(np.std(cv_res["test_r2"])), "mse_std": float(np.std(cv_res["test_neg_mse"])), "mae_std": float(np.std(cv_res["test_neg_mae"]))}
        except Exception:
            cv_mean = {}
            cv_std = {}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=42
        )

        model = LinearRegression(fit_intercept=self.fit_intercept)
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
            eval_artifacts = self.evaluate_model(model, X_train, X_test, y_train, y_test, is_classifier=False, feature_names=features)
            result.update(eval_artifacts)
        except Exception:
            pass
        return result
