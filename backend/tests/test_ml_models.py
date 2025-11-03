import numpy as np
import pandas as pd
from ..ml import (
    LinRegManager,
    LogRegManager,
    DecisionTreeManager,
    RandForestManager,
    BaggingManager,
    BoostingManager,
    NeuralNetManager,
    SVMManager,
)


def make_regression_df(n=200):
    rng = np.random.RandomState(42)
    x1 = rng.randn(n)
    x2 = rng.randn(n)
    y = 2.0 * x1 + 3.0 * x2 + rng.randn(n) * 0.1
    return pd.DataFrame({"x1": x1, "x2": x2, "y": y})


def make_classification_df(n=200):
    rng = np.random.RandomState(42)
    x1 = rng.randn(n)
    x2 = rng.randn(n)
    y = (x1 + x2 > 0).astype(int)
    return pd.DataFrame({"x1": x1, "x2": x2, "y": y})


def _is_number(x):
    return np.isscalar(x) and np.isfinite(x)


def test_regression_managers_run():
    df = make_regression_df()
    managers = [
        LinRegManager,
        DecisionTreeManager,
        RandForestManager,
        BaggingManager,
        BoostingManager,
        NeuralNetManager,
        SVMManager,
    ]

    for mgr_cls in managers:
        mgr = mgr_cls(df, test_split=20)
        result = mgr.train("y", ["x1", "x2"])

        assert "r2_score" in result, f"{mgr_cls.__name__} missing r2_score"
        assert "mse" in result, f"{mgr_cls.__name__} missing mse"
        assert _is_number(result["r2_score"])
        assert _is_number(result["mse"])


def test_logistic_manager_run():
    df = make_classification_df()
    mgr = LogRegManager(df, test_split=20)
    result = mgr.train("y", ["x1", "x2"])
    assert "accuracy" in result
    assert _is_number(result["accuracy"])
    assert 0.0 <= float(result["accuracy"]) <= 1.0
