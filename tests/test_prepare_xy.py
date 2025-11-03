import pandas as pd
from backend.ml import ModelManager, LogRegManager


def test_prepare_xy_classification():
    df = pd.DataFrame({
        'a': [1, 2, 3, None],
        'b': ['x', 'y', 'x', 'z'],
        'target': ['yes', 'no', 'yes', 'no']
    })
    mgr = LogRegManager(df, 20)
    X, y = mgr.prepare_xy(['a', 'b'], 'target', classifier=True)
    assert 'a' in X.columns and 'b' in X.columns
    assert y.dtype.name.startswith('int') or y.dtype.name == 'int64'


def test_prepare_xy_regression():
    df = pd.DataFrame({
        'a': [1.0, 2.5, None, 4.0],
        'b': ['1', '2', '3', '4'],
        'target': [0.5, 1.5, 2.0, None]
    })
    from backend.ml import LinRegManager
    mgr = LinRegManager(df, 25)
    X, y = mgr.prepare_xy(['a', 'b'], 'target', classifier=False)
    assert X.shape[0] == y.shape[0]
    assert y.dtype.name.startswith('float')
