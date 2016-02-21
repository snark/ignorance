#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'scandir'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='ignorance',
    version='0.1.0',
    description="A spec-compliant gitignore parser",
    long_description=readme + '\n\n' + history,
    author="Steve Cook",
    author_email='snarkout@gmail.com',
    url='https://github.com/snark/ignorance',
    packages=[
        'ignorance',
    ],
    package_dir={'ignorance':
                 'ignorance'},
    include_package_data=True,
    install_requires=requirements,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    license="ISCL",
    zip_safe=False,
    keywords='ignorance',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
