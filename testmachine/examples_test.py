import pytest
from .examples import (
    commutativeints, floats, nonuniquelists, unbalancedtrees
)


@pytest.mark.parametrize("example", [
    floats,
    nonuniquelists,
    unbalancedtrees,
])
def test_all_examples(example):
    machine = example.machine
    results = machine.run()
    assert len(results.log) > 0


def test_ints_are_commutative():
    assert commutativeints.machine.run() is None
