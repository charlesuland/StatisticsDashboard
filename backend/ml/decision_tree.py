import pandas as pd
from sklearn.metrics import r2_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

class DecisionTreeManager:
    def __init__(self, dataframe: pd.DataFrame, test_split):
        self.df = dataframe
        self.test_split = test_split / 100
    
    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        # Convert any object columns to numeric
        for col in X.select_dtypes(include='object').columns:
            try:
                X[col] = pd.to_numeric(X[col])
            except:
                X[col] = pd.Categorical(X[col]).codes

        # Convert y if needed
        if y.dtype == 'object':
            try:
                y = pd.to_numeric(y)
            except:
                y = pd.Categorical(y).codes

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split/100, random_state=42
        )

        model = DecisionTreeRegressor()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        return {"r2_score": r2_score(y_test, y_pred)}
