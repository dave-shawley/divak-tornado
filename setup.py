#!/usr/bin/env python

import os.path

import setuptools

import divak


def read_requirements(name):
    requirements = []
    with open(os.path.join('requires', name)) as req_file:
        for line in req_file:
            if '#' in line:
                line = line[0:line.index('#')]
            line = line.strip()
            if line.startswith('-r'):
                requirements.append(read_requirements(line[2:].strip()))
            elif line and not line.startswith('-'):
                requirements.append(line)
    return requirements


setuptools.setup(
    name='divak-tornado',
    version=divak.version,
    description='Observe the behavior of your Tornado code',
    long_description=open('README.rst', 'r').read(),
    license='BSD',
    author='Dave Shawley',
    author_email='daveshawley@gmail.com',
    url='https://github.com/dave-shawley/divak',
    packages=['divak'],
    install_requires=read_requirements('installation.txt'),
    tests_require=read_requirements('testing.txt'),
    test_suite='nose.collector',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
