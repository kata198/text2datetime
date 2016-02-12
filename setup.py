#!/usr/bin/env python

import os
import sys

from setuptools import setup

if __name__ == '__main__':

    summary = 'Python module which can convert an extensive number of ways to represent time with strings to datetime objects'

    # Ensure we are in the same directory as this setup.py
    dirName = os.path.dirname(__file__)
    if dirName and os.getcwd() != dirName:
        os.chdir(dirName)
    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except Exception as e:
        sys.stderr.write('Error reading description: %s\n' %(str(e),))
        long_description = summary

    setup(name='text2datetime',
        version='1.0.0',
        modules=['text2datetime'],
        packages=['text2datetime'],
        provides=['text2datetime'],
        install_requires=['python-dateutil'],
        requires=['python-dateutil'],
        keywords=['text2datetime', 'text', 'string', 'time', 'conversion', 'datetime', 'tomorrow', 'relative', 'date', 'convert'],
        url='https://github.com/kata198/text2datetime',
        long_description=long_description,
        author='Tim Savannah',
        author_email='kata198@gmail.com',
        maintainer='Tim Savannah',
        maintainer_email='kata198@gmail.com',
        license='LGPLv2',
        description=summary,
        classifiers=['Development Status :: 5 - Production/Stable',
            'Programming Language :: Python',
            'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ]
        
    )

#vim: set ts=4 sw=4 expandtab

