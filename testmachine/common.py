import operator
from .operations import (
    Drop,
    Swap,
    Rot,
    BinaryOperator,
    UnaryOperator,
    ReadAndWrite,
    Check,
    PushRandom,
)


def operation(*args, **kwargs):
    """
    Add an operation which pops arguments from each of the varstacks named
    in args, passes the result in that order to function and pushes the
    result of the invocation onto target. If target is None the result is
    ignored.
    """
    return ReadAndWrite(
        *args, **kwargs
    )


def binary_operation(*args, **kwargs):
    return BinaryOperator(*args, **kwargs)


def unary_operation(operation, varstack, name):
    return UnaryOperator(operation, varstack, name)


def check(*args, **kwargs):
    """
    Add an operation which reads from the varstacks in args in order,
    without popping their result and passes them in order to test. If test
    returns something truthy this operation passes, else it will fail.
    """
    return Check(*args, **kwargs)


def generate(*args, **kwargs):
    """
    Add a generator for operations which produces values by calling
    produce with a Random instance and pushes them onto target.
    """
    return PushRandom(*args, **kwargs)


def basic_operations(varstack):
    """
    Define basic stack shuffling and manipulation operations on varstack.
    Most testmachines will want these on most varstacks. They don't do
    anything very interesting, but by moving data around they expand the
    range of programs that can be generated.
    """
    return (
        Drop(varstack),
        Swap(varstack),
        Rot(varstack),
    )


def arithmetic_operations(varstack):
    """
    Elements of varstack may be combined with the integer operations +, -,
    * and /. They may also be negated.
    """
    return (
        binary_operation(operator.add, varstack, "+"),
        binary_operation(operator.sub, varstack, "-"),
        binary_operation(operator.mul, varstack, "*"),
        unary_operation(operator.neg, varstack, "-"),
    )


def ints(target="ints"):
    """
    Convenience function to define operations for filling target with ints.
    Defines some generators, and adds basic and arithmetic operations to target
    """
    return (
        basic_operations(target),
        arithmetic_operations(target),
        generate(lambda r: r.randint(0, 10 ** 6), target),
        generate(lambda r: r.randint(-10, 10), target),
    )


def lists(source, target):
    """
    Operations which populate target with lists whose elements come from source
    """
    return (
        basic_operations(target),
        generate(lambda r: [], target),
        operation(
            function=lambda x, y: x.append(y),
            argspec=(target, source),
            target=None,
            name="append",
            pattern="{0}.append({1})"
        ),
        operation(
            function=lambda x: [x],
            argspec=(source,),
            target=target,
            name="singleton",
            pattern="[{0}]",
        ),
        operation(
            function=lambda x, y: [x, y],
            argspec=(source, source),
            target=target,
            name="pair",
            pattern="[{0}, {1}]",
        ),
        operation(
            function=list,
            argspec=(target,),
            target=target
        ),
        binary_operation(operator.add, target, "+"),
    )
