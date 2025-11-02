import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

class MLManager:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
    
    def train_linear_regression(self, target_column: str):
        X = self.df.drop(columns=[target_column])
        y = self.df[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        
        return {
            "mse": mse,
            
        }