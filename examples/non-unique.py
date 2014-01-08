"""
Find an example demonstrating that lists can contain the same element multiple
times.

Example output:
    t1 = 354449
    t2 = []
    t2.append(t1)
    t3 = t2 + t2
    assert unique(t3)
"""

from testmachine import TestMachine

machine = TestMachine()

machine.ints("ints")
machine.lists(source="ints", target="intlists")
machine.check(
    lambda s: len(s) == len(set(s)), argspec=("intlists",), name="unique"
)

machine.run()
