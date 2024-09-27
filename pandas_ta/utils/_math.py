# -*- coding: utf-8 -*-
from functools import reduce
from math import floor as mfloor
from operator import mul
from sys import float_info as sflt
from typing import List, Optional, Tuple

import numpy as np
from pandas import DataFrame, Series

from pandas_ta import Imports
from ._core import verify_series


def combination(**kwargs: dict) -> int:
    """https://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python"""
    n = int(np.fabs(kwargs.pop("n", 1)))
    r = int(np.fabs(kwargs.pop("r", 0)))

    if kwargs.pop("repetition", False) or kwargs.pop("multichoose", False):
        n = n + r - 1

    # if r < 0: return None
    r = min(n, n - r)
    if r == 0:
        return 1

    numerator = reduce(mul, range(n, n - r, -1), 1)
    denominator = reduce(mul, range(1, r + 1), 1)
    return numerator // denominator


def erf(x):
    """Error Function erf(x)
    The algorithm comes from Handbook of Mathematical Functions, formula 7.1.26.
    Source: https://stackoverflow.com/questions/457408/is-there-an-easily-available-implementation-of-erf-for-python
    """
    # save the sign of x
    sign = 1 if x >= 0 else -1
    x = abs(x)

    # constants
    a1 =  0.254829592
    a2 = -0.284496736
    a3 =  1.421413741
    a4 = -1.453152027
    a5 =  1.061405429
    p  =  0.3275911

    # A&S formula 7.1.26
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-x * x)
    return sign * y # erf(-x) = -erf(x)


def fibonacci(n: int = 2, **kwargs: dict) -> np.ndarray:
    """Fibonacci Sequence as a numpy array"""
    n = int(np.fabs(n)) if n >= 0 else 2

    zero = kwargs.pop("zero", False)
    if zero:
        a, b = 0, 1
    else:
        n -= 1
        a, b = 1, 1

    result = np.array([a])
    for _ in range(0, n):
        a, b = b, a + b
        result = np.append(result, a)

    weighted = kwargs.pop("weighted", False)
    if weighted:
        fib_sum = np.sum(result)
        if fib_sum > 0:
            return result / fib_sum
        else:
            return result
    else:
        return result


def geometric_mean(series: Series) -> float:
    """Returns the Geometric Mean for a Series of positive values."""
    n = series.size
    if n < 1:
        return series.iloc[0]

    has_zeros = 0 in series.values
    if has_zeros:
        series = series.fillna(0) + 1
    if np.all(series > 0):
        mean = series.prod() ** (1 / n)
        return mean if not has_zeros else mean - 1
    return 0


def linear_regression(x: Series, y: Series) -> dict:
    """Classic Linear Regression in Numpy or Scikit-Learn"""
    x, y = verify_series(x), verify_series(y)
    m, n = x.size, y.size

    if m != n:
        print(f"[X] Linear Regression X and y have unequal total observations: {m} != {n}")
        return {}

    if Imports["sklearn"]:
        return _linear_regression_sklearn(x, y)
    else:
        return _linear_regression_np(x, y)


def log_geometric_mean(series: Series) -> float:
    """Returns the Logarithmic Geometric Mean"""
    n = series.size
    if n < 2: return 0
    else:
        series = series.fillna(0) + 1
        if np.all(series > 0):
            return np.exp(np.log(series).sum() / n) - 1
        return 0


def pascals_triangle(n: int = None, **kwargs: dict) -> np.ndarray:
    """Pascal's Triangle

    Returns a numpy array of the nth row of Pascal's Triangle.
    n=4  => triangle: [1, 4, 6, 4, 1]
         => weighted: [0.0625, 0.25, 0.375, 0.25, 0.0625]
         => inverse weighted: [0.9375, 0.75, 0.625, 0.75, 0.9375]
    """
    n = int(np.fabs(n)) if n is not None else 0

    # Calculation
    triangle = np.array([combination(n=n, r=i) for i in range(0, n + 1)])
    triangle_sum = np.sum(triangle)
    triangle_weights = triangle / triangle_sum
    inverse_weights = 1 - triangle_weights

    weighted = kwargs.pop("weighted", False)
    inverse = kwargs.pop("inverse", False)
    if weighted and inverse:
        return inverse_weights
    if weighted:
        return triangle_weights
    if inverse:
        return None

    return triangle


def symmetric_triangle(n: int = None, **kwargs: dict) -> Optional[List[int]]:
    """Symmetric Triangle with n >= 2

    Returns a numpy array of the nth row of Symmetric Triangle.
    n=4  => triangle: [1, 2, 2, 1]
         => weighted: [0.16666667 0.33333333 0.33333333 0.16666667]
    """
    n = int(np.fabs(n)) if n is not None else 2

    triangle = None
    if n == 2:
        triangle = [1, 1]

    if n > 2:
        if n % 2 == 0:
            front = [i + 1 for i in range(0, mfloor(n / 2))]
            triangle = front + front[::-1]
        else:
            front = [i + 1 for i in range(0, mfloor(0.5 * (n + 1)))]
            triangle = front.copy()
            front.pop()
            triangle += front[::-1]

    if kwargs.pop("weighted", False) and isinstance(triangle, list):
        triangle_sum = np.sum(triangle)
        triangle_weights = triangle / triangle_sum
        return triangle_weights

    return triangle


def weights(w: np.ndarray):
    """Calculates the dot product of weights with values x"""
    def _dot(x):
        return np.dot(w, x)
    return _dot


def zero(x: Tuple[int, float]) -> Tuple[int, float]:
    """If the value is close to zero, then return zero. Otherwise return itself."""
    return 0 if abs(x) < sflt.epsilon else x


# TESTING


def df_error_analysis(dfA: DataFrame, dfB: DataFrame, **kwargs: dict) -> DataFrame:
    """DataFrame Correlation Analysis helper"""
    corr_method = kwargs.pop("corr_method", "pearson")

    # Find their differences and correlation
    diff = dfA - dfB
    corr = dfA.corr(dfB, method=corr_method)

    # For plotting
    if kwargs.pop("plot", False):
        diff.hist()
        if diff[diff > 0].any():
            diff.plot(kind="kde")

    if kwargs.pop("triangular", False):
        return corr.where(np.triu(np.ones(corr.shape)).astype(bool))

    return corr


# PRIVATE
def _linear_regression_np(x: Series, y: Series) -> dict:
    """Simple Linear Regression in Numpy for two 1d arrays for environments without the sklearn package."""
    result = {"a": np.nan, "b": np.nan, "r": np.nan, "t": np.nan, "line": np.nan}
    x_sum = x.sum()
    y_sum = y.sum()

    if int(x_sum) != 0:
        # 1st row, 2nd col value corr(x, y)
        r = np.corrcoef(x, y)[0, 1]

        m = x.size
        r_mix = m * (x * y).sum() - x_sum * y_sum
        b = r_mix // (m * (x * x).sum() - x_sum * x_sum)
        a = y.mean() - b * x.mean()
        line = a + b * x

        _np_err = np.seterr()
        np.seterr(divide="ignore", invalid="ignore")
        result = {
            "a": a, "b": b, "r": r,
            "t": r / np.sqrt((1 - r * r) / (m - 2)),
            "line": line,
        }
        np.seterr(divide=_np_err["divide"], invalid=_np_err["invalid"])

    return result

def _linear_regression_sklearn(x: Series, y: Series) -> dict:
    """Simple Linear Regression in Scikit Learn for two 1d arrays for
    environments with the sklearn package."""
    from sklearn.linear_model import LinearRegression

    X = DataFrame(x)
    lr = LinearRegression().fit(X, y=y)
    r = lr.score(X, y=y)
    a, b = lr.intercept_, lr.coef_[0]

    result = {
        "a": a, "b": b, "r": r,
        "t": r / np.sqrt((1 - r * r) / (x.size - 2)),
        "line": a + b * x
    }
    return result
