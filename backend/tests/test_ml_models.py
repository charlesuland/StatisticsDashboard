import numpy as np
import pandas as pd
from ml import (
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


# helper to instantiate managers robustly
def _instantiate(mgr_cls, df, test_split=20, classifier_flag=None):
    try:
        if classifier_flag is None:
            return mgr_cls(df, test_split=test_split)
        return mgr_cls(df, test_split=test_split, classifier=classifier_flag)
    except TypeError:
        # fallback for managers that don't accept `classifier` kw
        return mgr_cls(df, test_split=test_split)


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
        # request classifier=False when supported
        mgr = _instantiate(mgr_cls, df, test_split=20, classifier_flag=False)
        result = mgr.train("y", ["x1", "x2"])

        # new contract: result is a dict with top-level metrics (no "test" wrapper)
        assert isinstance(result, dict), f"{mgr_cls.__name__} should return a dict"

        # expect top-level metrics
        # test-set metrics
        print(result)
        assert "r2" in result, f"{mgr_cls.__name__} missing r2"
        assert "mse" in result, f"{mgr_cls.__name__} missing mse"
        assert _is_number(result["r2"])
        assert _is_number(result["mse"])


def test_classification_managers_run():
    df = make_classification_df()
    classifier_managers = [
        LogRegManager,
        DecisionTreeManager,
        RandForestManager,
        BaggingManager,
        BoostingManager,
        NeuralNetManager,
        SVMManager,
    ]

    for mgr_cls in classifier_managers:
        # for LogRegManager (classifier-only) classifier_flag is ignored by _instantiate
        mgr = _instantiate(mgr_cls, df, test_split=20, classifier_flag=True)
        result = mgr.train("y", ["x1", "x2"])

        print(result)
        assert isinstance(result, dict), f"{mgr_cls.__name__} should return a dict"
        # test-set classifier metrics (top-level)
        assert "accuracy" in result, f"{mgr_cls.__name__} missing accuracy"
        assert _is_number(result["accuracy"])
        assert 0.0 <= float(result["accuracy"]) <= 1.0