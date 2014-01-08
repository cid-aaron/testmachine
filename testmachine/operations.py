from operator import itemgetter
from collections import defaultdict
from random import Random


class OperationOrLanguage(object):
    precondition = None

    def applicable(self, context):
        for varstack, req in self.requirements.items():
            if not context.varstack(varstack).has(req):
                return False
        if self.precondition:
            return self.precondition(*context.read(self.argspec))
        else:
            return True


class Operation(OperationOrLanguage):
    def __init__(self, varstacks, name=None, pattern=None, precondition=None):
        """
        varstacks :: [(str, int)]

        Create an operation which works on these varstacks requiring them to
        have height at least this high.
        """
        self.varstacks = tuple(map(itemgetter(0), varstacks))
        self.name = name or self.__class__.__name__.lower()
        self.requirements = defaultdict(lambda: 0)
        for s, c in varstacks:
            self.requirements[s] += c
        self.pattern = pattern
        self.precondition = precondition

    def __repr__(self):
        return "Operation(%s)" % self.display()

    def compile(self, arguments, results):
        if self.pattern is None:
            invocation = "%s(%s)" % (self.name, ', '.join(arguments))
        else:
            invocation = self.pattern % arguments

        if results:
            return ["%s = %s" % (', '.join(results), invocation)]
        else:
            return [invocation]

    def args(self):
        return self.varstacks

    def display(self):
        return "%s(%s)" % (
            self.name, ', '.join(map(repr, self.args()))
        )

    def invoke(self, context):
        raise NotImplementedError()


class ReadAndWrite(Operation):
    def __init__(
        self, function, argspec, target=None, name=None, precondition=None,
        pattern=None
    ):
        super(ReadAndWrite, self).__init__(
            _counts(argspec),
            name or function.__name__,
            pattern=pattern,
            precondition=precondition,
        )
        self.function = function
        self.argspec = argspec
        self.target = target

    def invoke(self, context):
        args = [context.varstack(n).pop() for n in self.argspec]
        result = self.function(*args)
        if self.target is not None:
            context.varstack(self.target).push(result)


class Mutate(Operation):
    def __init__(
        self, function, argspec, name=None, precondition=None,
        pattern=None
    ):
        super(ReadAndWrite, self).__init__(
            _counts(argspec),
            name or function.__name__,
            pattern=pattern,
            precondition=precondition,
        )


class BinaryOperator(ReadAndWrite):
    def __init__(self, operation, varstack, name, precondition=None):
        super(BinaryOperator, self).__init__(
            function=operation,
            argspec=(varstack, varstack),
            target=varstack,
            name=name,
            precondition=precondition,
        )

    def compile(self, arguments, results):
        assert len(arguments) == 2
        assert len(results) <= 1
        x, y = arguments
        invocation = " ".join((x, self.name, y))
        if results:
            return ["%s = %s" % (', '.join(results), invocation)]
        else:
            return [invocation]


class UnaryOperator(ReadAndWrite):
    def __init__(self, operation, varstack, name):
        super(UnaryOperator, self).__init__(
            function=operation,
            argspec=(varstack,),
            target=varstack,
            name=name
        )

    def compile(self, arguments, results):
        assert len(arguments) == 1
        assert len(results) <= 1
        invocation = "".join((self.name, arguments[0]))
        if results:
            return ["%s = %s" % (', '.join(results), invocation)]
        else:
            return [invocation]


class Check(Operation):
    def __init__(self, test, argspec, name=None, pattern=None):
        name = name or test.__name__
        if not pattern:
            arg_string = ', '.join(["%s"] * len(argspec))
            pattern = "assert %s(%s)" % (name, arg_string)

        super(Check, self).__init__(
            _counts(argspec), name=name, pattern=pattern
        )
        self.argspec = argspec
        self.test = test

    def compile(self, arguments, results):
        assert not results
        return [self.pattern % arguments]

    def invoke(self, context):
        args = context.read(self.argspec)
        assert self.test(*args)


class SingleStackOperation(Operation):
    min_height = 0

    def __init__(self, varstack, name=None):
        super(SingleStackOperation, self).__init__(
            varstacks=((varstack, self.min_height),), name=name
        )

    @property
    def varstack(self):
        return self.varstacks[0]


class Push(SingleStackOperation):
    def __init__(self, varstack, gen_value):
        super(Push, self).__init__(varstack, name="push")
        self.gen_value = gen_value

    def compile(self, arguments, results):
        assert not arguments
        assert len(results) == 1
        return ["%s = %r" % (results[0], self.gen_value())]

    def invoke(self, context):
        context.varstack(self.varstack).push(self.gen_value())

    def args(self):
        return super(Push, self).args() + (self.gen_value(),)


class InapplicableLanguage(Exception):
    pass


class Language(OperationOrLanguage):
    def __init__(self):
        self.requirements = {}

    def generate(self, context):
        """
        Given a runcontext Context produce an Operation or raise
        InapplicableLanguage if this Language cannot produce Operations in the
        current state of context.

        This should always throw InapplicableLanguage if the requirements are
        not satisfied. It may throw it in other circumstances.
        """
        raise NotImplementedError()


class PushRandom(Language):
    def __init__(self, produce, target, name=None):
        super(PushRandom, self).__init__()
        self.produce = produce
        self.target = target

    def generate(self, context):
        state = context.random.getstate()

        def gen_result():
            r = Random(0)
            r.setstate(state)
            return self.produce(r)
        return Push(
            self.target,
            gen_result,
        )


class ChooseFrom(Language):
    def __init__(self, children):
        super(ChooseFrom, self).__init__()
        self.children = tuple(children)
        self.requirements = defaultdict(lambda: 0)
        for c in children:
            for k, v in c.requirements.items():
                self.requirements[k] = min(v, self.requirements[k])

    def generate(self, context):
        children = list(self.children)
        context.random.shuffle(children)
        for child in children:
            if isinstance(child, Language):
                try:
                    return child.generate(context)
                except InapplicableLanguage:
                    continue
            else:
                if child.applicable(context):
                    return child
        raise InapplicableLanguage


class Dup(SingleStackOperation):
    min_height = 1

    def invoke(self, context):
        context.varstack(self.varstack).dup()

    def compile(self, arguments, results):
        return []


class Drop(SingleStackOperation):
    min_height = 1

    def invoke(self, context):
        context.varstack(self.varstack).pop()

    def compile(self, arguments, results):
        return []


class Swap(SingleStackOperation):
    min_height = 2

    def invoke(self, context):
        vs = context.varstack(self.varstack)
        x = vs.pop()
        y = vs.pop()
        vs.push(x)
        vs.push(y)

    def compile(self, arguments, results):
        return []


class Rot(SingleStackOperation):
    min_height = 3

    def invoke(self, context):
        vs = context.varstack(self.varstack)
        x = vs.pop()
        y = vs.pop()
        z = vs.pop()
        vs.push(y)
        vs.push(z)
        vs.push(x)

    def compile(self, arguments, results):
        return []


def _counts(values):
    c = defaultdict(lambda: 0)
    for v in values:
        c[v] += 1
    return c.items()
