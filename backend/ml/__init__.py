from .ModelManager import ModelManager
from .linear_regression import LinRegManager
from .logistic_regression import LogRegManager
from .bagging import BaggingManager
from .boosting import BoostingManager
from .decision_tree import DecisionTreeManager
from .neural_net import NeuralNetManager
from .random_forest import RandForestManager
from .support_vector_machine import SVMManager

# expose classes at package level for `from ..ml import LinRegManager`
__all__ = [
    "ModelManager",
    "LinRegManager",
    "LogRegManager",
    "DecisionTreeManager",
    "BaggingManager",
    "BoostingManager",
    "RandForestManager",
    "NeuralNetManager",
    "SVMManager",
]

# models registry used by routes.modelEval: keys should match frontend values
models = {
    "linear_regression": LinRegManager,
    "logistic_regression": LogRegManager,
    "decision_tree": DecisionTreeManager,
    "random_forest": RandForestManager,
    "rf": RandForestManager,
    "svm": SVMManager,
    "support_vector_machine": SVMManager,  
    "bagging": BaggingManager,
    "boosting": BoostingManager,
    "neural_net": NeuralNetManager,
    "custom_dnn": NeuralNetManager,   
    "user_defined_dnn": NeuralNetManager, 
}


