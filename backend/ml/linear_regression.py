import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from . import ModelManager


class LinRegManager(ModelManager):
    def __init__(self, dataframe: pd.DataFrame, test_split, fit_intercept: bool = True):
        self.df = self.sanitize(dataframe)
        self.test_split = test_split / 100
        self.fit_intercept = fit_intercept

    # renamed to `train` to match abstract interface and use self.test_split
    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=42
        )

        model = LinearRegression(fit_intercept=self.fit_intercept)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        return {
            "r2": float(r2_score(y_test, y_pred)),
            "mse": float(mean_squared_error(y_test, y_pred)),
            "mae": float(mean_absolute_error(y_test, y_pred)),
        }
