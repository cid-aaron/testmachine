"""
Example with an entirely user defined datatype. We are constructing a binary
tree and we want it to be balanced in the sense that given a split, each of
the child nodes differ in the number of nodes they contain by at most one.
Unfortunately we forgot to implement the code for doing that. Silly us. We need
testmachine to remind us of this fact.

Example output:

    t1 = Leaf()
    t2 = Leaf()
    t3 = Leaf()
    t4 = t3.join(t2)
    t5 = t4.join(t4)
    t6 = t5.join(t1)
    assert t6.balanced()
"""

from testmachine import TestMachine
from testmachine.common import basic_operations, check, generate, operation


# Our tree type is a classic binary tree
class Tree(object):
    def join(self, other):
        return Join(self, other)


class Leaf(Tree):
    def balanced(self):
        return True

    def __len__(self):
        return 1

    def __repr__(self):
        return "Leaf()"


class Join(Tree):
    def __init__(self, child0, child1):
        self.child0 = child0
        self.child1 = child1

    def __repr__(self):
        return "Join(%r, %r)" % (self.child0, self.child1)

    def __len__(self):
        return len(self.child0) + len(self.child1)

    def balanced(self):
        if not (self.child0.balanced() and self.child1.balanced()):
            return False

        return (
            (len(self.child0) <= len(self.child1) + 1) and
            (len(self.child1) <= len(self.child0) + 1)
        )


# Business as usual
machine = TestMachine()

# Because we might as well
machine.add(basic_operations("trees"))

# We can always generate leaf nodes. We ignore the Random argument we're given
# because all Leaves are created equal.
machine.add(generate(lambda _: Leaf(), "trees"))


# Given two trees, we can join them together into a new tree
machine.add(operation(
    argspec=("trees", "trees"),
    target="trees",
    function=lambda x, y: x.join(y),
    pattern="{0}.join({1})"
))

# Assert that our trees are balanced.
machine.add(check(
    test=lambda x: x.balanced(),
    argspec=("trees",),
    # The pattern argument controls the output formatting when emitting an
    # example. It will be formatted with the name of the variable we are
    # checking.
    pattern="assert {0}.balanced()"
))

if __name__ == '__main__':
    machine.main()
