"""
Find an example demonstrating that floating point addition is not associative

Example output:
    t1 = 0.11945064104636571
    t2 = t1 / t1
    t3 = 0.16278913131835504
    t4 = 0.6323432862008465
    assert associative_add(t4, t3, t2)
"""

from testmachine import TestMachine
from random import Random

machine = TestMachine()

machine.basic_operations("floats")
machine.arithmetic_operations("floats")
machine.generate(Random.random, "floats")


def associative_add(x, y, z):
    return x + (y + z) == (x + y) + z

machine.check(associative_add, ("floats", "floats", "floats"))

machine.run()
