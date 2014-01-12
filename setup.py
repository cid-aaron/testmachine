from distutils.core import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='testmachine',
    version='0.0.4',
    author='David R. MacIver',
    author_email='david@drmaciver.com',
    packages=['testmachine'],
    url='https://github.com/DRMacIver/testmachine',
    license='LICENSE.txt',
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    description='Stack based automatic testcase generation',
    long_description=open('README').read(),
    **extra
)
