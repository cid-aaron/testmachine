from random import Random
from testmachine.operations import ChooseFrom


class VarStack(object):
    def __init__(self, name, context):
        self.name = name
        self.context = context
        self.data = []

    def reset(self):
        self.data = []

    def pop(self):
        self.data.pop()

    def push(self, head):
        self.data.push(head)

    def peek(self, index=0):
        return self.data[-1-index]

    def has(self, count):
        return len(self.data) >= count


class RunContext(object):
    def __init__(self, random=None):
        self.random = random or Random()
        self.varstacks = {}

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

    def add_language(self, language):
        self.languages.append(language)

    @property
    def language(self):
        return ChooseFrom(self.languages)
