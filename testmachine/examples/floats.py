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

# This is the object that we use to define the kind of test case we want to
# generate.
machine = TestMachine()

# testmachine.common defines a number of standard operations on different types
# of variables. We're going to use some of those rather than implementing our
# own.
from testmachine.common import (
    basic_operations, arithmetic_operations, generate, check
)

# We only have one type of variable. We'll call that floats, but this is just
# an arbitrary name. We could call it steve if we wanted to.
# We generate our basic floats as random numbers between 0 and 1.
machine.add(generate(Random.random, "floats"))

# These are basic stack manipulation operations. They aren't very exciting, but
# they expand the likelihood of producing interesting programs. Most machines
# will use these.
machine.add(basic_operations("floats"))

# floats can be combined with the normal arithmetic operations
machine.add(arithmetic_operations("floats"))


# We want to demonstrate that floating point addition is not associative. This
# check will read three variables off our stack of floats and see if adding t
# them up in different orders produces the same value.
def associative_add(x, y, z):
    return x + (y + z) == (x + y) + z

# If the function we pass to a check returns a falsy value then the program
# will fail.
machine.add(check(associative_add, ("floats", "floats", "floats")))

if __name__ == '__main__':
    # Attempt to find a falsifying example for the problem we've defined and
    # print it to stdout. If this cannot find any examples (it will), say so.
    machine.main()
