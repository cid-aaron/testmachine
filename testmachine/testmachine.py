from random import Random
from contextlib import contextmanager
from .operations import (
    ChooseFrom,
    ReadAndWrite,
    Check,
    PushRandom
)


class FrozenVarStack(Exception):
    def __init__(self):
        super(FrozenVarStack, self).__init__("Cannot modify frozen varstack")


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

    def pop(self):
        if self.frozen:
            raise FrozenVarStack()

        self._integrity_check()
        result = self.data.pop()
        self.context.read(self.names.pop())
        return result

    def push(self, head):
        if self.frozen:
            raise FrozenVarStack()
        self._integrity_check()
        self.data.append(head)
        self.names.append(self.context.newvar())

    def peek(self, index=0):
        self._integrity_check()
        i = -1 - index
        self.context.read(self.names[i])
        return self.data[i]

    def has(self, count):
        self._integrity_check()
        return len(self.data) >= count


class RunContext(object):
    def __init__(self, random=None):
        self.random = random or Random()
        self.varstacks = {}
        self.var_index = 0

    def __repr__(self):
        return "RunContext(%s)" % (
            ', '.join(
                "%s=%r" % (v.name, len(v.data))
                for v in self.varstacks.values()
            )
        )

    def newvar(self):
        self.var_index += 1
        return self.var_index

    def read(self, var):
        pass

    def write(self, var):
        pass

    def varstack(self, name):
        try:
            return self.varstacks[name]
        except KeyError:
            varstack = VarStack(name, self)
            self.varstacks[name] = varstack
            return varstack


class TestMachine(object):
    def __init__(self):
        self.languages = []

    def operation(self, function, args, target=None, name=None):
        """
        Add an operation which pops arguments from each of the varstacks named
        in args, passes the result in that order to function and pushes the
        result of the invocation onto target. If target is None the result is
        ignored.
        """
        self.add_language(ReadAndWrite(
            function=function, argorder=args, target=target, name=name
        ))

    def check(self, test, args, name=None):
        """
        Add an operation which reads from the varstacks in args in order,
        without popping their result and passes them in order to test. If test
        returns something truthy this operation passes, else it will fail.
        """
        self.add_language(Check(test=test, args=args, name=name))

    def generate(self, produce, target, name=None):
        """
        Add a generator for operations which produces values by calling
        produce with a Random instance and pushes them onto target.
        """
        self.add_language(
            PushRandom(produce=produce, target=target, name=name)
        )

    def add_language(self, language):
        self.languages.append(language)

    @property
    def language(self):
        return ChooseFrom(self.languages)

    def find_failing_program(self, n_iters=500, prog_length=200):
        for _ in xrange(n_iters):
            program = []
            context = RunContext()
            try:
                for _ in xrange(prog_length):
                    operation = self.language.generate(context)
                    program.append(operation)
                    operation.invoke(context)
            except:
                return program

    def run_program(self, program):
        context = RunContext()
        for operation in program:
            operation.invoke(context)
        return context

    def program_fails(self, program):
        try:
            self.run_program(program)
            return False
        except:
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
            except:
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

    def run(self, steps=1000):
        first_try = self.find_failing_program(prog_length=steps)
        return self.minimize_failing_program(first_try)
