from typing import Literal
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.model_selection import train_test_split

from numpy.typing import ArrayLike


class NeuralNetManager:
    def __init__(
        self,
        dataframe: pd.DataFrame,
        test_split,
        hidden_layer_sizes: ArrayLike = [100],
        activation: Literal["relu", "identity", "logistic", "tanh"] = "relu",
        solver: Literal["lbfgs", "sgd", "adam"] = "adam",
        lr: float = .001,
        max_iter: int = 500,
        random_state: int = 42,
        classifier: bool = False,
    ):
        self.df = dataframe
        self.test_split = test_split / 100
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation
        self.solver = solver
        self.max_iter = max_iter
        self.lr = lr
        self.random_state = random_state
        self.classifier = classifier

    def train(self, target, features):
        X = self.df[features].copy()
        y = self.df[target].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_split, random_state=self.random_state
        )

        if self.classifier:
            model = MLPClassifier(
                hidden_layer_sizes=self.hidden_layer_sizes,
                activation=self.activation,
                solver=self.solver,
                max_iter=self.max_iter,
                learning_rate_init=self.lr,
                random_state=self.random_state,
            )
        else:
            model = MLPRegressor(
                hidden_layer_sizes=self.hidden_layer_sizes,
                activation=self.activation,
                solver=self.solver,
                max_iter=self.max_iter,
                learning_rate_init=self.lr,
            )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        if self.classifier:
            return {"accuracy": accuracy_score(y_test, y_pred)}
        return {"r2_score": r2_score(y_test, y_pred), "mse": mean_squared_error(y_test, y_pred)}
