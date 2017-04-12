from setuptools import setup

import os
import sys
import re

install_requires = []
if sys.version_info < (2, 7):
    raise Exception("health-stats requires Python 2.y or higher.")
elif sys.version_info < (3, 0):
    install_requires += ['future']

install_requires += ['pretty', 'plotly', 'pytz', 'sqlalchemy', 'unicodecsv', 'dateparser']

# Load the version by reading prep.py, so we don't run into
# dependency loops by importing it into setup.py
version = None
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'health_stats', '__init__.py')) as file:
    for line in file:
        m = re.search(r'__version__\s*=\s*(.+?\n)', line)
        if m:
            version = eval(m.group(1))
            break

setup_args = dict(
    name='health-stats',
    version=version,
    author='Chris Petersen',
    author_email='geek@ex-nerd.com',
    url='https://github.com/ex-nerd/health-stats',
    license='MIT',
    description='Python utilities for parsing/graphing health-related data like weight, blood pressure, blood glucose, etc.',
    long_description=open('README.md').read(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'parse-health-stats = health_stats.cli:parse',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
)

if __name__ == '__main__':
    setup(**setup_args)
