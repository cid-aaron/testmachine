import operator
from .operations import (
    Dup,
    Drop,
    Swap,
    Rot,
)


def basic_operations(machine, varstack):
    """
    Define basic stack shuffling and manipulation operations on varstack.
    Most testmachines will want these on most varstacks. They don't do
    anything very interesting, but by moving data around they expand the
    range of programs that can be generated.
    """
    machine.add_language(Dup(varstack))
    machine.add_language(Drop(varstack))
    machine.add_language(Swap(varstack))
    machine.add_language(Rot(varstack))


def arithmetic_operations(machine, varstack):
    """
    Elements of varstack may be combined with the integer operations +, -,
    * and /. They may also be negated.
    """
    machine.binary_operation(operator.add, varstack, "+")
    machine.binary_operation(operator.sub, varstack, "-")
    machine.binary_operation(operator.mul, varstack, "*")
    machine.unary_operation(operator.neg, varstack, "-")


def ints(machine, target="ints"):
    """
    Convenience function to define operations for filling target with ints.
    Defines some generators, and adds basic and arithmetic operations to target
    """
    basic_operations(machine, target)
    arithmetic_operations(machine, target)
    machine.generate(lambda r: r.randint(0, 10 ** 6), target)
    machine.generate(lambda r: r.randint(-10, 10), target)


def lists(machine, source, target):
    """
    Operations which populate target with lists whose elements come from source
    """
    basic_operations(machine, target)
    machine.generate(lambda r: [], target)
    machine.operation(
        function=lambda x, y: x.append(y),
        argspec=(target, source),
        target=None,
        name="append",
        pattern="%s.append(%s)"
    )
    machine.operation(
        function=lambda x: [x],
        argspec=(source,),
        target=target,
        name="singleton",
        pattern="[%s]",
    )
    machine.operation(
        function=lambda x, y: [x, y],
        argspec=(source, source),
        target=target,
        name="pair",
        pattern="[%s, %s]",
    )
    machine.operation(
        function=list,
        argspec=(target,),
        target=target
    )
    machine.binary_operation(operator.add, target, "+")
