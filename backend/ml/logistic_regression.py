import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

class LogRegManager:
    def __init__(self, dataframe: pd.DataFrame, test_split):
        self.df = dataframe
        self.test_split = test_split / 100
    
    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=42
        )

        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        return {"accuracy": accuracy_score(y_test, y_pred)}
