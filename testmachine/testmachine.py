from __future__ import print_function
from random import Random
from contextlib import contextmanager
from .operations import (
    ChooseFrom,
    ReadAndWrite,
    Check,
    PushRandom,
    BinaryOperator,
    UnaryOperator,
)
from collections import namedtuple, defaultdict
import traceback


ProgramStep = namedtuple(
    "ProgramStep",
    ("definitions", "arguments", "operation")
)


class TestMachineError(Exception):
    pass


class FrozenVarStack(TestMachineError):
    def __init__(self):
        super(FrozenVarStack, self).__init__("Cannot modify frozen varstack")


class NoFailingProgram(TestMachineError):
    pass


class VarStack(object):
    def __init__(self, name, context):
        self.name = name
        self.context = context
        self.data = []
        self.names = []
        self.frozen = False

    def _integrity_check(self):
        assert len(self.data) == len(self.names)

    @contextmanager
    def freeze(self):
        self.frozen = True
        try:
            yield
        finally:
            self.frozen = False

    def modification(self):
        if self.frozen:
            raise FrozenVarStack()

    def pop(self):
        self.modification()
        self._integrity_check()
        result = self.data.pop()
        self.context.on_read(self.names.pop())
        return result

    def push(self, head):
        self.modification()
        self._integrity_check()
        self.data.append(head)
        v = self.context.newvar()
        self.names.append(v)
        self.context.on_write(v)

    def dup(self):
        self.modification()
        self._integrity_check()
        self.names.append(self.names[-1])
        self.data.append(self.data[-1])

    def peek(self, index=0):
        self._integrity_check()
        i = -1 - index
        self.context.on_read(self.names[i])
        return self.data[i]

    def has(self, count):
        self._integrity_check()
        return len(self.data) >= count


class RunContext(object):
    def __init__(self, random=None):
        self.random = random or Random()
        self.varstacks = {}
        self.var_index = 0
        self.reset_tracking()
        self.log = []

    def reset_tracking(self):
        self.values_read = []
        self.values_written = []

    def run_program(self, program):
        for operation in program:
            self.execute(operation)

    def execute(self, operation):
        self.reset_tracking()
        try:
            operation.invoke(self)
            self.log.append(ProgramStep(
                operation=operation,
                definitions=tuple(self.values_written),
                arguments=tuple(self.values_read)
            ))
        except Exception:
            self.log.append(ProgramStep(
                operation=operation,
                definitions=(),
                arguments=tuple(self.values_read)
            ))
            raise

    def __repr__(self):
        return "RunContext(%s)" % (
            ', '.join(
                "%s=%r" % (v.name, len(v.data))
                for v in self.varstacks.values()
            )
        )

    def newvar(self):
        self.var_index += 1
        return "t%d" % (self.var_index,)

    def on_read(self, var):
        self.values_read.append(var)

    def on_write(self, var):
        self.values_written.append(var)

    def varstack(self, name):
        try:
            return self.varstacks[name]
        except KeyError:
            varstack = VarStack(name, self)
            self.varstacks[name] = varstack
            return varstack

    def read(self, argspec):
        result = []
        seen = defaultdict(lambda: 0)
        for a in argspec:
            result.append(self.varstack(a).peek(seen[a]))
            seen[a] += 1
        return tuple(result)


class TestMachine(object):
    def __init__(
        self,
        n_iters=500,
        prog_length=1000,
        good_enough=10,
        print_output=True,
    ):
        self.languages = []
        self.n_iters = n_iters
        self.prog_length = prog_length
        self.good_enough = good_enough
        self.print_output = print_output

    def inform(self, message, *args, **kwargs):
        assert not (args and kwargs)
        if self.print_output:
            print(message % (args or kwargs))

    def operation(self, *args, **kwargs):
        """
        Add an operation which pops arguments from each of the varstacks named
        in args, passes the result in that order to function and pushes the
        result of the invocation onto target. If target is None the result is
        ignored.
        """
        self.add_language(ReadAndWrite(
            *args, **kwargs
        ))

    def check(self, *args, **kwargs):
        """
        Add an operation which reads from the varstacks in args in order,
        without popping their result and passes them in order to test. If test
        returns something truthy this operation passes, else it will fail.
        """
        self.add_language(Check(*args, **kwargs))

    def generate(self, produce, target, name=None, supports_copy=True):
        """
        Add a generator for operations which produces values by calling
        produce with a Random instance and pushes them onto target.
        """
        self.add_language(
            PushRandom(produce=produce, target=target, name=name)
        )

    def run(self):
        """
        run this testmachine and attempt to produce a failing program. Returns
        None if no such program is found, else will return a RunContext which
        has executed up to the first failure.

        If self.print_output is True then this will print a nice representation
        of the group to stdout and the exception generated by the failure.
        """
        try:
            first_try = self.find_failing_program()
        except NoFailingProgram as e:
            self.inform(e.message)
            return
        minimal = self.minimize_failing_program(first_try)
        context = RunContext()
        try:
            context.run_program(minimal)
        except Exception:
            pass

        for step in context.log:
            statements = step.operation.compile(
                arguments=step.arguments, results=step.definitions
            )
            for statement in statements:
                self.inform(statement)

        if self.print_output:
            try:
                self.run_program(minimal)
                assert False, "This program should be failing but isn't"
            except Exception:
                traceback.print_exc()

        return context

    def add_language(self, language):
        self.languages.append(language)

    @property
    def language(self):
        return ChooseFrom(self.languages)

    def find_failing_program(
        self,
    ):
        examples_found = 0
        best_example = None

        for _ in range(self.n_iters):
            program = []
            context = RunContext()
            for _ in xrange(self.prog_length):
                operation = self.language.generate(context)
                program.append(operation)
                try:
                    operation.invoke(context)
                except Exception:
                    examples_found += 1
                    if (
                        (best_example is None) or
                        (len(program) < len(best_example))
                    ):
                        best_example = program
                    if examples_found >= self.good_enough:
                        return best_example
                    else:
                        break
        if best_example is None:
            raise NoFailingProgram(
                ("Unable to find a failing program of length <= %d"
                 " after %d iterations") % (self.prog_length, self.n_iters)
            )
        return best_example

    def run_program(self, program):
        context = RunContext()
        context.run_program(program)
        return context

    def program_fails(self, program):
        try:
            self.run_program(program)
            return False
        except Exception:
            return True

    def prune_program(self, program):
        context = RunContext()
        results = []
        for operation in program:
            if not operation.applicable(context):
                continue
            results.append(operation)
            try:
                operation.invoke(context)
            except Exception:
                break

        return results

    def minimize_failing_program(self, program):
        assert self.program_fails(program)
        current_best = program
        while True:
            for i in xrange(len(current_best)):
                edit = list(current_best)
                del edit[i]
                pruned_edit = self.prune_program(edit)
                if self.program_fails(pruned_edit):
                    current_best = pruned_edit
                    break
                if i < len(edit):
                    del edit[i]
                    pruned_edit = self.prune_program(edit)
                    if self.program_fails(pruned_edit):
                        current_best = pruned_edit
                        break
            else:
                return current_best

    def binary_operation(self, *args, **kwargs):
        self.add_language(
            BinaryOperator(*args, **kwargs)
        )

    def unary_operation(self, operation, varstack, name):
        self.add_language(
            UnaryOperator(operation, varstack, name)
        )
