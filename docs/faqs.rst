====
FAQs
====

.. contents:: Table of Contents

Introduction
============

What is pysocket?
------------------

pysocket is a high-level library, built on the socket module, to easily program
sockets with `Python <http://www.python.org/>`__.

What is Python?
---------------

Python is an interpreted, interactive, object-oriented, easy-to-learn
programming language. It is often compared to *Tcl, Perl, Scheme* or *Java*.

Installing and compatibility
============================

How do I install pysocket?
---------------------------

If you are not new to Python you probably don't need that, otherwise follow the
`install instructions <install.html>`__.

Which Python versions are compatible?
-------------------------------------

pysocket should work with Python *2.4* to *3.5*.

How about PyPy? Is it supported?
--------------------------------
pysocket should also work with PyPy *2.4* to *3.5*.

On which platforms can pysocket be used?
-----------------------------------------

pysocket should work on any platform which Python runs on, because it only
requires Python installed to run. The best way to know whether pysocket works
on your platform is installing it and running its test suite.

Implementation
==============

Starting from pysocket v0.3 onwards, pysocket implements nearly everything the
socket module has, with some extras.

For more information, check the `Socket module's docs <https://docs.python.org/2/library/socket.html>`__. 

Differences with the socket module
----------------------------------

Here are some notable differences. The first one is that, when binding a socket, the format in
pysocket is:

.. code-block:: python

    sock.bind('', 8000)

But with the socket module:

.. code-block:: python

    sock.bind(('', 8000))

Which, in my opinion, doesn't look as nice as the first example.

The second diffrence is that the accept function doesn't return anything, but
instead, it processes that data itself. Here's how you would call it with
pysocket:

.. code-block:: python

    sock.accept()

Whereas, in the socket module, you would write:

.. code-block:: python

    conn, addr = sock.accept()

If you really need the info, you can do this with pysocket:

.. code-block:: python

    conn, addr = socket.accept(True)

Which waits until it gets a request, and then it returns the data.

