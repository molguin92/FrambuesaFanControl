#!/usr/bin/python3
import threading

import click
import smbus
import RPi.GPIO as GPIO
import os
import time
from threading import Thread

from loguru import logger

from fan_curves import SimpleSmoothFanCurve

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


# defaults
TEMP_PATH = "/sys/class/thermal/thermal_zone0/temp"
FAN_ADDR = 0x1A


def read_temperature() -> float:
    try:
        with open(TEMP_PATH, "r") as fp:
            temp = fp.read()

        return int(temp) / 1000.0
    except IOError:
        return -1.0


def set_fan_speed(percent: int) -> None:
    rev = GPIO.RPI_REVISION
    if rev in (2, 3):
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)

    bus.write_byte(FAN_ADDR, max(min(percent, 100), 0))


if __name__ == "__main__":
    logger.info("Monitoring temperature and adjusting fan speed in real time...")
    curve = SimpleSmoothFanCurve(min_temp=40, max_temp=55, order=2, min_fan=5)
    while True:
        temp = read_temperature()
        logger.info(f"Temperature: {temp} C°")
        fan_speed = curve.get_fan_percent(temp)
        logger.info(f"Setting fan to {fan_speed}%")
        set_fan_speed(fan_speed)
        time.sleep(5)
