import pytest
from testmachine import TestMachine


def test_does_not_hide_error_in_generate():
    def broken(r):
        raise ValueError()

    machine = TestMachine()

    machine.generate(broken, "broken")
    with pytest.raises(ValueError):
        machine.run()
