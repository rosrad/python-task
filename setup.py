from setuptools import setup, find_packages

PACKAGE = "task"
NAME = "task"
DESCRIPTION = "task manager for experiments and save result into nosql or excel"
AUTHOR = "Bo Ren"
AUTHOR_EMAIL = "justnow.ren@gmail.com"
URL = "https://github.com/rosrad/python-task"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(exclude=["tests.*", "tests"]),
)

