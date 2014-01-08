"""
Find an example demonstrating that lists can contain the same element multiple
times.

Example output:
    t1 = 1
    t2 = [t1, t1]
    assert unique(t2)
"""

from testmachine import TestMachine

machine = TestMachine()

machine.ints("ints")
machine.lists(source="ints", target="intlists")
machine.check(
    lambda s: len(s) == len(set(s)), argspec=("intlists",), name="unique"
)

machine.run()
