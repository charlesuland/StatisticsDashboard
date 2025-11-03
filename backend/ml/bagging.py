import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.ensemble import BaggingRegressor
from sklearn.model_selection import train_test_split

class BaggingManager:
    def __init__(self, dataframe: pd.DataFrame, test_split):
        self.df = dataframe
        self.test_split = test_split / 100

    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=42
        )

        model = BaggingRegressor()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        return {"r2_score": r2_score(y_test, y_pred), "mse": mean_squared_error(y_test, y_pred)}
