import copy
from operator import itemgetter


class Operation(object):
    def __init__(self, varstacks):
        """
        varstacks :: [(str, int)]

        Create an operation which works on these varstacks requiring them to
        have height at least this high.
        """
        self.stacks = tuple(map(itemgetter(0), varstacks))
        self.requirements = dict(varstacks)

    def run(self, context):
        self.invoke(map(context.varstack, self.stacks.keys()))

    def applicable(self, context):
        for varstack, req in self.requirements.items():
            if not context.varstack(varstack).has(req):
                return False
        return True

    def invoke(self, *args):
        raise NotImplemented()


class SingleStackOperation(object):
    def __init__(self, varstack):
        super(SingleStackOperation, self).__init__(
            varstacks=(varstack,)
        )


class InapplicableLanguage(Exception):
    pass


class Language(object):
    def generate(self, context):
        """
        Given a runcontext Context produce an Operation or raise
        InapplicableLanguage if this Language cannot produce Operations in the
        current state of context
        """
        raise NotImplemented()

    def requirements(self):
        raise NotImplemented()


class Push(Operation):
    def __init__(self, varstack, value):
        super(Push, self).__init__((varstack,))
        self.value = value

    def invoke(self, stack):
        stack.push(self.value)


class PushRandom(Language):
    def __init__(self, varstack, produce=None):
        self.varstack = varstack
        if produce is not None:
            self.produce = produce

    def requirements(self):
        return {}

    def produce(self, random):
        raise NotImplemented()

    def generate(self, context):
        return Push(self.stack, self.produce(context.random))


class ChooseFrom(Language):
    def __init__(self, children):
        self.children = tuple(children)

    def generate(self, context):
        children = list(self.children)
        context.random.shuffle(children)
        for child in children:
            if isinstance(context, Language):
                try:
                    return child.generate(context)
                except InapplicableLanguage:
                    continue
            else:
                if child.applicable(context):
                    return child
        raise InapplicableLanguage


class Just(Language):
    def __init__(self, generator):
        self.generator = generator

    def generate(self, context):
        return self.generator


class DropWithDestroy(SingleStackOperation):
    def __init__(self, stack, args=(), destroy=None):
        super(Drop).__init__(stack, args)
        self.stack = stack
        self.destroy = destroy

    def invoke(self, stack):
        x = stack.pop()
        if self.destroy:
            self.destroy(x)


def Drop(stack):
    return DropWithDestroy(stack, lambda x: ())


class DupWithCopy(Operation):
    def __init__(self, stack, copy=copy.deepcopy):
        super(DupWithCopy, self).__init__(
            stacks=(stack,)
        )

    def invoke(self):
        self.stack.push(self.copy(self.stack.peek(0)))


class Swap(SingleStackOperation):
    def invoke(self, stack):
        x = stack.pop()
        y = stack.pop()
        stack.push(y)
        stack.push(x)


def Dup(stack):
    return DupWithCopy(stack, copy=lambda x: x)
