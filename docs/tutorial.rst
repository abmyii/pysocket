========
Tutorial
========

.. contents:: Table of Contents

Below is a set of example scripts showing some of the possible programs
which can be made with pysocket.  Some of them are included in
`examples <https://github.com/abmyii/pysocket/blob/master/examples/>`__
directory of pysocket source distribution. Of course, sockets are a big area,
so the examples are quite basic.

Starting a Simple socket
------------------------

pysocket isn't much different to the socket module, but there are one or two
different things when starting a socket. Here's how I might start it with the
socket module.

.. code-block:: python

    from socket import socket, SOCK_DGRAM

    sock = socket(type=SOCK_DGRAM)
    sock.setsockopt(1, 6, 1)
    sock.bind(('localhost', 8000))  # 127.0.0.1:8000

And here's how you might do the exact same thing with pysocket.

.. code-block:: python

    from pysocket import socket

    sock = pysocket.socket()  # SOCK_DGRAM is defaulted & sockopt is set
    sock.bind()  # 127.0.0.1:8000 is defaulted

So there you have it. Way simpler in pysocket.

Building a Simple server
------------------------

pysocket has a built-in server and client base class, which can be used with
minimal setup. Here's an example of how to use it

.. code-block:: python

    from pysocket import Server

    server = Server(('', 8000))  # 127.0.0.1:8000

    server.serve()  # asynchronous serving.

    # ... some time passes
    server.quit()

This receives data and sends it to all of the clients. Here is another simple example:

   # Echo server program
   import pysocket

   HOST = ''                 # Symbolic name meaning all available interfaces
   PORT = 50007              # Arbitrary non-privileged port
   s = pysocket.socket(pysocket.AF_INET, pysocket.SOCK_STREAM)
   s.bind(HOST, PORT)
   s.listen(1)
   conn, addr = s.accept(True)
   print('Connected by', addr)
   while True:
       data = conn.recv(1024)
       if not data: break
       conn.sendall(data)
   conn.close()

::

   # Echo client program
   import pysocket

   HOST = ''                 # The remote host
   PORT = 50007              # The same port as used by the server
   s = pysocket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.connect(HOST, PORT)
   s.sendall(b'Hello, world')
   data = s.recv(1024)
   s.close()
   print('Received', repr(data))

