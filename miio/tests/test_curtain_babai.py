from typing import Any, Dict, List
from unittest import TestCase

import pytest

from miio import CurtainBabai

from .dummies import DummyMiotDevice


class DummyCurtainBabai(DummyMiotDevice, CurtainBabai):
    def __init__(self, *args, **kwargs):
        self.state = {
            "motor_control": 0,
            "current_position": 100,
            "target_position": 100,
            "mode": 0,
        }

        self.return_values = {
            "get_prop": self._get_state,
            "get_properties": self.get_property_value_mock,
        }

        self.test_mapping = {
            f"{v.get('siid')}-{v.get('piid')}": k for k, v in self.mapping.items()
        }

        super().__init__(*args, **kwargs)

    def get_property_value_mock(self, x: List[Dict[str, Any]]) -> Any:
        r = x.pop()
        key = f"{r.get('siid')}-{r.get('piid')}"
        prop_name = self.test_mapping.get(key)
        data = [x for x in self.state if x["did"] == prop_name]
        for x in data:
            x["did"] = key
        return data

    def set_config(self, x):
        key, value = x
        config_mapping = {"cfg_lan_ctrl": "lan_ctrl", "cfg_save_state": "save_state"}

        self._set_state(config_mapping[key], [value])

    def set_open(self):
        key = "current_position"
        self.state = [
            {"did": key, "value": 100, "code": 0} if r["did"] == key else r
            for r in self.state
        ]

    def set_close(self):
        key = "current_position"
        self.state = [
            {"did": key, "value": 0, "code": 0} if r["did"] == key else r
            for r in self.state
        ]


@pytest.fixture(scope="class")
def dummycurtainbabai(request):
    request.cls.device = DummyCurtainBabai()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("dummycurtainbabai")
class TestCurtainBabai(TestCase):
    def test_on(self):
        self.device.set_close()  # make sure we are off
        assert self.device.status().is_opened is False

        self.device.set_open()
        assert self.device.status().is_opened is True

    def test_off(self):
        self.device.set_open()  # make sure we are on
        assert self.device.status().is_opened is True

        self.device.set_close()
        assert self.device.status().is_opened is False

    # def test_hard(self):
    #     x = CurtainBabai(ip='192.168.1.145', token='')
    #     r = x.status()
    #     assert r.status == MotorControl.Pause
    #     x.set_open()
    #     assert x.current_position > 0
    #     x.set_close()
    #     assert x.current_position < 100
