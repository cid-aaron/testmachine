"""
This attempts to show that integer addition is not commutative. Since integer
addition is commutative, it will not have much luck.

Example output:
    t1 = 0.11945064104636571
    t2 = t1 / t1
    t3 = 0.16278913131835504
    t4 = 0.6323432862008465
    assert associative_add(t4, t3, t2)
"""

from testmachine import TestMachine
import testmachine.common as common

machine = TestMachine()
common.ints(machine)


def commutative_add(x, y):
    return x + y == y + x

machine.check(commutative_add, ("ints", "ints"))

if __name__ == '__main__':
    machine.run()
