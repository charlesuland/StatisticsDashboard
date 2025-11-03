import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

class LinRegManager:
    def __init__(self, dataframe: pd.DataFrame, test_split):
        self.df = dataframe
        self.test_split = test_split / 100

    # renamed to `train` to match abstract interface and use self.test_split
    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=42
        )

        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        return {"r2_score": r2_score(y_test, y_pred), "mse": mean_squared_error(y_test, y_pred)}
