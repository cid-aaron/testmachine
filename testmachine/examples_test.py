import pytest
from .examples import (
    floats, nonuniquelists, unbalancedtrees
)


@pytest.mark.parametrize("example", [
    floats,
    nonuniquelists,
    unbalancedtrees,
])
def test_all_examples(example):
    machine = example.machine
    machine.print_output = False
    results = machine.run()
    assert len(results.log) > 0
