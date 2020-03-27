#!/usr/bin/env python

from setuptools import setup

setup(
    name='pysocket',
    version='1.0.0',
    description='A high-level socket module extension',
    author='abmyii (@abmyii)',
    author_email='abmyii@protonmail.com',
    url='https://github.com/abmyii/pysocket',
    packages=['pysocket'],
      long_description="""\
      pysocket is a high-level extension on the low-level
      socket module, with some improvments and tweaks.
      """,
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          'Programming Language :: Python :: 3',
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Topic :: Software Development :: Libraries",
    ],
    keywords='socket python-standard-library',
    license='MIT',
)
