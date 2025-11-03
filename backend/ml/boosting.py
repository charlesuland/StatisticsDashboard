import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score
from sklearn.ensemble import AdaBoostRegressor, AdaBoostClassifier
from sklearn.model_selection import train_test_split


class BoostingManager:
    def __init__(
        self,
        dataframe: pd.DataFrame,
        test_split,
        n_estimators: int = 50,
        learning_rate: float = 1.0,
        random_state: int = 42,
        classifier: bool = False,
    ):
        self.df = dataframe
        self.test_split = test_split / 100
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.classifier = classifier

    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=self.random_state
        )

        if self.classifier:
            model = AdaBoostClassifier(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                random_state=self.random_state,
            )
        else:
            model = AdaBoostRegressor(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                random_state=self.random_state,
            )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        if self.classifier:
            return {"accuracy": accuracy_score(y_test, y_pred)}
        return {"r2_score": r2_score(y_test, y_pred), "mse": mean_squared_error(y_test, y_pred)}
