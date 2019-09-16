# import pytest
from appdaemontestframework import automation_fixture
from apps.motion_lights import MotionLight
from datetime import time


@automation_fixture(MotionLight)
def motion_light(given_that):
    given_that.passed_arg("motion_sensor").is_set_to("binary_sensor.motion")
    given_that.passed_arg("light").is_set_to("light.test_light")
    given_that.passed_arg("timeout").is_set_to(120)


def test_callback_registered(given_that, motion_light, assert_that):
    assert_that(motion_light).listens_to.state(
        "binary_sensor.motion", new="on"
    ).with_callback(motion_light.motion_callback)


def test_light_on_off(given_that, motion_light, time_travel, assert_that):
    motion_light.is_light_times = lambda: True
    motion_light.motion_callback(None, None, None, None, None)
    assert_that("light.test_light").was.turned_on()
    time_travel.fast_forward(2).minutes()
    assert_that("light.test_light").was.turned_off()
