from abc import ABCMeta, abstractmethod
from typing import Any, Optional

import pandas as pd
import pandas.api.types as ptypes


class ModelManager(metaclass=ABCMeta):
    def __init__(self, dataframe: pd.DataFrame, test_split: int):
        self.df = self.sanitize(dataframe)
        self.test_split = test_split / 100

    @abstractmethod
    def train(self, target, features, *args, **kwargs) -> dict[str, Any]:
        pass

    def sanitize(self, df: Optional[pd.DataFrame] = None, drop_threshold: float = 0.5) -> pd.DataFrame:
        if df is None:
            # if called before self.df exists, just return an empty DataFrame defensive
            df = getattr(self, "df", pd.DataFrame())
        df = df.copy()

        # Drop duplicate rows
        df = df.drop_duplicates().reset_index(drop=True)

        # Drop columns with too many missing values
        if len(df) > 0:
            thresh = int((1.0 - drop_threshold) * len(df))
            if thresh <= 0:
                thresh = 1
            df = df.dropna(axis=1, thresh=thresh)

        # Process object columns: try datetime -> numeric -> categorical codes
        obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
        for col in obj_cols:
            series = df[col]
            # try parse datetime (prefer datetimes only if a reasonable fraction parse)
            try:
                parsed = pd.to_datetime(series, errors="coerce")
                if parsed.notna().sum() >= max(1, int(0.5 * len(df))):
                    df[col] = parsed
                    continue
            except Exception:
                pass

            # try numeric coercion
            coerced = pd.to_numeric(series, errors="coerce")
            if coerced.notna().sum() > 0:
                df[col] = coerced
            else:
                # fallback to categorical codes (ensure integer dtype)
                codes = pd.Categorical(series).codes
                # convert codes (which may be -1 for NaN) to int64
                df[col] = pd.Series(codes, index=df.index, dtype="int64")

        # Ensure datetime columns are native numpy datetime64[ns]
        for col in df.columns:
            if ptypes.is_datetime64_any_dtype(df[col]) or ptypes.is_datetime64tz_dtype(df[col]):
                df[col] = pd.to_datetime(df[col], errors="coerce", utc=False)

        # Convert datetime columns to numeric epoch seconds to avoid dtype mixing
        datetime_cols = [c for c in df.columns if ptypes.is_datetime64_any_dtype(df[c]) or ptypes.is_datetime64tz_dtype(df[c])]
        for c in datetime_cols:
            # astype('int64') gives ns since epoch; convert to seconds as float64
            try:
                df[c] = df[c].astype("int64") / 1e9
            except Exception:
                # fallback: coerce then convert
                df[c] = pd.to_datetime(df[c], errors="coerce").astype("int64") / 1e9
            # ensure float dtype
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")

        # Normalize numeric dtypes to float64 to avoid nullable-int / float promotion issues
        num_cols = [c for c in df.columns if ptypes.is_numeric_dtype(df[c])]
        if num_cols:
            df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").astype("float64")

        # Fill numeric NaNs with column mean (after conversion to float64)
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
