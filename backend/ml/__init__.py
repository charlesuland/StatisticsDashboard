from abc import ABCMeta, abstractmethod
from typing import Any
import pandas as pd

from .linear_regression import LinRegManager
from .logistic_regression import LogRegManager
from .bagging import BaggingManager
from .boosting import BoostingManager
from .decision_tree import DecisionTreeManager
from .neural_net import NeuralNetManager
from .random_forest import RandForestManager
from .support_vector_machine import SVMManager

# [x] linear regression
# [ ] logistic regression
# [ ] decision trees
# [ ] bagging
# [ ] boosting
# [ ] random forests
# [ ] support vector machines
# [ ] user defined deep neural networks


models = {
    "linear_regression": LinRegManager,
    "logistic_regression": LogRegManager,
    "bagging": BaggingManager,
    "boosting": BoostingManager,
    "decision_tree": DecisionTreeManager,
    "neural_net": NeuralNetManager,
    "random_forest": RandForestManager,
    "support_vector_machine": SVMManager,
}


class ModelManager(metaclass=ABCMeta):
    def __init__(self, dataframe: pd.DataFrame, test_split: int):
        self.df = dataframe
        self.test_split = test_split / 100

    @abstractmethod
    def train(self, target, features, *args, **kwargs) -> dict[str, Any]:
        pass
