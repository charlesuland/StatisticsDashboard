from abc import ABCMeta, abstractmethod
from typing import Any, Optional
import pandas as pd

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


class ModelManager(metaclass=ABCMeta):
    def __init__(self, dataframe: pd.DataFrame, test_split: int):
        self.df = self.sanitize(dataframe)
        self.test_split = test_split / 100


    @abstractmethod
    def train(self, target, features, *args, **kwargs) -> dict[str, Any]:
        pass

    def sanitize(self, df: pd.DataFrame, drop_threshold: float = 0.5) -> pd.DataFrame:
        if df is None:
            df = self.df
        df = df.copy()

        # Drop duplicate rows
        df = df.drop_duplicates().reset_index(drop=True)

        # Drop columns with too many missing values
        if len(df) > 0:
            thresh = int((1.0 - drop_threshold) * len(df))
            if thresh <= 0:
                # keep at least one non-null required to keep column
                thresh = 1
            df = df.dropna(axis=1, thresh=thresh)

        # Process object columns: try datetime -> numeric -> categorical codes
        obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
        for col in obj_cols:
            series = df[col]
            # try parse datetime
            try:
                parsed = pd.to_datetime(series, errors="coerce")
                if parsed.notna().sum() >= int(0.5 * len(df)):
                    df[col] = parsed
                    continue
            except Exception:
                pass
            # try numeric coercion
            coerced = pd.to_numeric(series, errors="coerce")
            if coerced.notna().sum() > 0:
                df[col] = coerced
            else:
                # fallback to categorical codes
                df[col] = pd.Categorical(series).codes

        # Fill numeric NaNs with column mean
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        for col in num_cols:
            if df[col].isna().any():
                try:
                    mean_val = float(df[col].mean(skipna=True))
                except Exception:
                    mean_val = 0.0
                df[col] = df[col].fillna(mean_val)

        # Reset index and return
        df = df.reset_index(drop=True)
        return df
