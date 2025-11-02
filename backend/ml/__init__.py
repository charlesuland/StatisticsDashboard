from abc import ABCMeta, abstractmethod
from linear_regression import LinRegManager
import pandas as pd

models = {
    "linear_regression": LinRegManager,

}

class ModelManager(metaclass=ABCMeta):
    def __init__(self, dataframe: pd.DataFrame, test_split):
        self.df = dataframe
        self.test_split = test_split / 100
        

    @abstractmethod
    def train(self, target, features, *args, **kwargs):
        pass