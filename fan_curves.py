import abc
import warnings
from typing import Callable

import numpy as np
import scipy.optimize as opt


class BaseFanCurve(abc.ABC):
    def __init__(
        self,
        min_temp: float,
        max_temp: float,
        min_fan: int = 0,
        max_fan: int = 100,
    ):
        self._min_temp = min_temp
        self._max_temp = max_temp
        self._min_fan = min_fan
        self._max_fan = max_fan

    @abc.abstractmethod
    def _get_fan_percent(self, temp: float) -> int:
        pass

    def get_fan_percent(self, temp: float) -> int:
        if temp < self._min_temp:
            return self._min_fan
        elif temp > self._max_temp:
            return self._max_fan
        else:
            val = int(self._get_fan_percent(temp))
            return max(0, min(100, val))


def make_exp_function(order: int) -> Callable[[float, float, float], float]:
    def _exp_fn(x, a, b) -> float:
        return np.float_power(x + a, order) * b

    return _exp_fn


class SimpleSmoothFanCurve(BaseFanCurve):
    """
    Fits a smooth curve of fan values, such that the at temp <= <min_temp> the fan
    spins at <min_fan>, and at temp >= <max_temp>, the fan spins at <max_temp>.

    The fan curve can be of any order, but not all order values yield possible
    solutions.

    Examples of different curves for min_temp = 30, max_temp = 60, and min_fan = 0,
    max_fan = 100 [temperature -> fan speed]:

        - Linear curve (order = 1): 30C -> 0%; 40C -> 34%; 50C -> 67%; 60C -> 100%.

        - Quadratic curve (order = 2): 30C -> 1%; 40C -> 12%; 50C -> 45%; 60C -> 100%.

        - Cubic curve (order = 3): 30C -> 1%; 40C -> 4%; 50C -> 30%; 60C -> 100%.

        - Square root curve (order = 0.5): 30C -> 1%; 40C -> 56%; 50C -> 79%; 60C ->
        97%.

    """

    def __init__(
        self,
        min_temp: float,
        max_temp: float,
        min_fan: int = 0,
        max_fan: int = 100,
        order: int | float = 1,
    ):
        super(SimpleSmoothFanCurve, self).__init__(
            min_temp=min_temp,
            max_temp=max_temp,
            min_fan=min_fan,
            max_fan=max_fan,
        )

        # fit an exponential curve to the values such that the fan is <min_fan> at
        # the <min_temp> and <max_fan> at <max_temp>

        # solve the equation
        self._exp_fn = make_exp_function(order)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # don't want to see optimization warnings

            (self._a, self._b), *_ = opt.curve_fit(
                self._exp_fn, (min_temp, max_temp), (min_fan, max_fan)
            )

    def _get_fan_percent(self, temp: float) -> int:
        return int(np.ceil(self._exp_fn(temp, self._a, self._b)))


if __name__ == "__main__":
    curve = SimpleSmoothFanCurve(min_temp=30, max_temp=60, order=0.33)

    for i in range(30, 65, 10):
        print(f"{i}C -> {curve.get_fan_percent(i)}%;", end=" ")
