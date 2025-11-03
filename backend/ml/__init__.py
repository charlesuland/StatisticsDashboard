
from.ModelManager import ModelManager
from .linear_regression import LinRegManager
from .logistic_regression import LogRegManager
from .bagging import BaggingManager
from .boosting import BoostingManager
from .decision_tree import DecisionTreeManager
from .neural_net import NeuralNetManager
from .random_forest import RandForestManager
from .support_vector_machine import SVMManager

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


