import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score
from sklearn.ensemble import BaggingRegressor, BaggingClassifier
from sklearn.model_selection import train_test_split


class BaggingManager:
    def __init__(
        self,
        dataframe: pd.DataFrame,
        test_split,
        n_estimators: int = 10,
        max_samples: float | int = 1.0,
        random_state: int = 42,
        classifier: bool = False,
    ):
        self.df = dataframe
        self.test_split = test_split / 100
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.random_state = random_state
        self.classifier = classifier

    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=self.random_state
        )

        if self.classifier:
            model = BaggingClassifier(
                n_estimators=self.n_estimators,
                max_samples=self.max_samples,
                random_state=self.random_state,
            )
        else:
            model = BaggingRegressor(
                n_estimators=self.n_estimators,
                max_samples=self.max_samples,
                random_state=self.random_state,
            )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        if self.classifier:
            return {"accuracy": accuracy_score(y_test, y_pred)}
        return {"r2_score": r2_score(y_test, y_pred), "mse": mean_squared_error(y_test, y_pred)}
