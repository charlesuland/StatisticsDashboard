import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.model_selection import train_test_split


class DecisionTreeManager:
    def __init__(
        self,
        dataframe: pd.DataFrame,
        test_split,
        max_depth: int | None = None,
        min_samples_split: int = 2,
        random_state: int = 42,
        classifier: bool = False,
    ):
        self.df = dataframe
        self.test_split = test_split / 100
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.random_state = random_state
        self.classifier = classifier

    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=self.random_state
        )

        if self.classifier:
            model = DecisionTreeClassifier(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                random_state=self.random_state,
            )
        else:
            model = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                random_state=self.random_state,
            )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        if self.classifier:
            return {"accuracy": accuracy_score(y_test, y_pred)}
        return {
            "r2_score": r2_score(y_test, y_pred),
            "mse": mean_squared_error(y_test, y_pred),
        }
