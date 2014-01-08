from operator import itemgetter
from collections import Counter


class OperationOrLanguage(object):
    def applicable(self, context):
        for varstack, req in self.requirements.items():
            if not context.varstack(varstack).has(req):
                return False
        return True


class Operation(OperationOrLanguage):
    def __init__(self, varstacks, name):
        """
        varstacks :: [(str, int)]

        Create an operation which works on these varstacks requiring them to
        have height at least this high.
        """
        self.varstacks = tuple(map(itemgetter(0), varstacks))
        self.name = name
        self.requirements = Counter()
        for s, c in varstacks:
            self.requirements[s] += c

    def __repr__(self):
        return "Operation(%s)" % self.display()

    def compile(self, arguments, results):
        invocation = "%s(%s)" % (self.name, ', '.join(arguments))
        if results:
            return ["%s = %s" % (', '.join(results), invocation)]
        else:
            return [invocation]

    def args(self):
        return self.varstacks

    def display(self, varnames=None):
        return "%s(%s)" % (
            self.name, ', '.join(map(repr, self.args(varnames)))
        )

    def invoke(self, context):
        raise NotImplementedError()


class ReadAndWrite(Operation):
    def __init__(self, function, argorder, target=None, name=None):
        super(ReadAndWrite, self).__init__(
            Counter(s for ss in (argorder, (target,)) for s in ss).items(),
            name or function.__name__
        )
        self.function = function
        self.argorder = argorder
        self.target = target

    def invoke(self, context):
        args = [context.varstack(n).pop() for n in self.argorder]
        result = self.function(*args)
        if self.target is not None:
            context.varstack(self.target).push(result)


class Check(Operation):
    def __init__(self, test, args, name=None):
        super(Check, self).__init__(
            Counter(args).items(), name or test.__name__
        )
        self.argorder = args
        self.test = test

    def compile(self, arguments, results):
        assert not results
        return ["assert %s(%s)" % (self.name, ', '.join(arguments))]

    def invoke(self, context):
        seen = Counter()
        args = []
        for a in self.argorder:
            args.append(context.varstack(a).peek(seen[a]))
            seen[a] += 1
        assert self.test(*args)


class SingleStackOperation(Operation):
    def __init__(self, varstack, name):
        super(SingleStackOperation, self).__init__(
            varstacks=(varstack,), name=name
        )

    @property
    def varstack(self):
        return self.varstacks[0]


class Push(SingleStackOperation):
    def __init__(self, varstack, value):
        super(Push, self).__init__((varstack, 0), name="push")
        self.value = value

    def compile(self, arguments, results):
        assert not arguments
        assert len(results) == 1
        return ["%s = %r" % (results[0], self.value)]

    def invoke(self, context):
        context.varstack(self.varstack).push(self.value)

    def args(self):
        return super(Push, self).args() + (self.value,)


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
        return Push(
            self.target,
            self.produce(context.random)
        )


class ChooseFrom(Language):
    def __init__(self, children):
        super(ChooseFrom, self).__init__()
        self.children = tuple(children)
        self.requirements = Counter()
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
