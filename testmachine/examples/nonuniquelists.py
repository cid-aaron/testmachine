"""
Find an example demonstrating that lists can contain the same element multiple
times.

Example output:
    t1 = 1
    t2 = [t1, t1]
    assert unique(t2)
"""

from testmachine import TestMachine
from testmachine.common import ints, lists, check

machine = TestMachine()

machine.add(
    # Populate the ints varstack with integer values
    ints(),
    # Populate the intlists varstack with lists whose elements are drawn from
    # the ints varstack
    lists(source="ints", target="intlists"),
    # Check whether a list contains only unique elements. If it contains
    # duplicates raise an error.
    check(
        lambda s: len(s) == len(set(s)), argspec=("intlists",), name="unique"
    ),
)

if __name__ == '__main__':
    # Find a program that creates a list with non-unique elements.
    machine.main()
