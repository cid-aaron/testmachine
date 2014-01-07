from distutils.core import setup
import sys

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='testmachine',
    version='0.0.1',
    author='David R. MacIver',
    author_email='david@drmaciver.com',
    packages=['testmachine'],
    url='https://github.com/DRMacIver/testmachine',
    license='LICENSE.txt',
    description='Stack based automatic testcase generation',
    long_description=open('README').read(),
    **extra
)
