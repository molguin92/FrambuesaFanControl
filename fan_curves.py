import abc
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


class ExponentialFanCurve(BaseFanCurve):
    def __init__(
        self,
        min_temp: float,
        max_temp: float,
        min_fan: int = 0,
        max_fan: int = 100,
        order: int = 3,
    ):
        super(ExponentialFanCurve, self).__init__(
            min_temp=min_temp,
            max_temp=max_temp,
            min_fan=min_fan,
            max_fan=max_fan,
        )

        # fit an exponential curve to the values such that the fan is <min_fan> at
        # the <min_temp> and <max_fan> at <max_temp>

        # solve the equation
        self._exp_fn = make_exp_function(order)
        (self._a, self._b), *_ = opt.curve_fit(
            self._exp_fn, (min_temp, max_temp), (min_fan, max_fan)
        )

    def _get_fan_percent(self, temp: float) -> int:
        return int(np.ceil(self._exp_fn(temp, self._a, self._b)))


if __name__ == "__main__":
    curve = ExponentialFanCurve(min_temp=30, max_temp=60)

    for i in range(30, 65, 5):
        print(curve.get_fan_percent(i))
