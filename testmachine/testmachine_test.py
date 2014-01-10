import pytest
from testmachine import TestMachine
from .common import generate


def test_does_not_hide_error_in_generate():
    def broken(r):
        raise ValueError()

    machine = TestMachine()
    machine.add(generate(broken, "broken"))
    with pytest.raises(ValueError):
        machine.run()
