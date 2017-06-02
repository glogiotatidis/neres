#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pip
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


requirements = [str(item.req) for item in
                pip.req.parse_requirements('requirements.txt',
                                           session=pip.download.PipSession())
                if item.req]

test_requirements = [
    str(item.req) for item in
    pip.req.parse_requirements('requirements_dev.txt',
                               session=pip.download.PipSession())
    if item.req]


setup(
    name='neres',
    version='0.4.0',
    description="(unofficial) NewRelic Synthetics CLI",
    long_description=readme + '\n\n' + history,
    author="Giorgos Logiotatidis",
    author_email='giorgos@sealabs.net',
    url='https://github.com/glogiotatidis/neres',
    packages=[
        'neres',
    ],
    package_dir={'neres':
                 'neres'},
    entry_points={
        'console_scripts': [
            'neres=neres.cli:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='neres',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
