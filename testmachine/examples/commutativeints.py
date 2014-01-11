"""
This attempts to show that integer addition is not commutative. Since integer
addition is commutative, it will not have much luck.

Example output:
    Unable to find a failing program of length <= 200 after 500 iterations
"""

from testmachine import TestMachine
from testmachine.common import ints, check

machine = TestMachine()

machine.add(
    ints()
)


def commutative_add(x, y):
    return x + y == y + x

machine.add(
    check(commutative_add, ("ints", "ints"))
)

if __name__ == '__main__':
    machine.main()
