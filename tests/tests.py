#!/usr/bin/env python
import unittest
import sys
import os

try:
    import pysocket
except ImportError:
    sys.path.append('..')
    import pysocket

class Tests(unittest.TestCase):

    def setUp(self):
        self.socket = pysocket.socket(type=2)
        self.new_socket = pysocket.socket(type=2)

    def tearDown(self):
        self.socket.close()
        self.new_socket.close()

    def test_binding(self):
        self.socket.bind()
        assert self.socket._is_server == True
        assert self.socket._binded == True

    def test_blocking(self):
        self.socket.add_blocked('127.0.0.1')
        assert len(self.socket._blocked) == 1

    def test_check_socket_type(self):
        assert self.socket.type() == 2

    def test_close(self):
        self.socket.close()
        assert self.socket._binded == False

    def test_connect(self):
        assert self.socket.connect('127.0.0.1', 1234) == None

    def test_disconn_client(self):
        self.socket.bind('127.0.0.1', 12345)
        self.new_socket.bind(port=8000)  # Binds to 127.0.0.1:8000
        self.new_socket.connect('127.0.0.1', 12345)
        assert self.socket.disconnect_client('127.0.0.1', 8000) == None

    def test_dup(self):
        dup = self.socket.dup()
        assert dup.type() == self.socket.type()
        dup.close()

    def test_get_client(self):
        self.socket.bind('127.0.0.1', 12345)
        self.new_socket.bind(port=8000)  # Binds to 127.0.0.1:8000
        self.new_socket.connect('127.0.0.1', 12345)
        self.socket.recv()
        assert self.socket.get_client('127.0.0.1') == ('127.0.0.1', 8000)

    def test_get_ip(self):
        self.socket.bind('127.0.0.1', 12345)
        assert self.socket.get_ip() == '127.0.0.1'

    def test_get_port(self):
        self.socket.bind('127.0.0.1', 12345)
        assert self.socket.get_port() == 12345

    def test_getclients(self):
        self.socket.bind('127.0.0.1', 12345)
        self.new_socket.bind(port=8000)  # Binds to 127.0.0.1:8000
        self.new_socket.connect('127.0.0.1', 12345)
        self.socket.recv()
        assert self.socket.getclients() == [('127.0.0.1', 8000)]

    def test_getpeerinfo(self):
        self.socket.bind('127.0.0.1', 12345)
        self.new_socket.bind(port=8000)  # Binds to 127.0.0.1:8000
        self.new_socket.connect('127.0.0.1', 12345)
        self.socket.recv()
        assert self.new_socket.getpeerinfo() == ('127.0.0.1', 12345)

    def test_getsockname(self):
        assert self.new_socket.getsockname() == ('0.0.0.0', 0)  # Default for an unbinded socket

    def test_getsockopt(self):
        if not sys.version_info[0] is 3:
            assert self.socket.getsockopt(1, 6, 1) == '\x01'
        else:
            assert self.socket.getsockopt(1, 6, 1) == b'\x01'

    def test_gettimeout(self):
        assert self.socket.gettimeout() == 0.5

    def test_leave(self):
        self.socket.bind('127.0.0.1', 12345)
        self.new_socket.bind(port=8000)  # Binds to 127.0.0.1:8000
        self.new_socket.connect('127.0.0.1', 12345)
        self.socket.recv()
        assert self.socket.get_client('127.0.0.1') == ('127.0.0.1', 8000)
        self.new_socket.leave()
        self.socket.recv()
        assert len(self.socket.getclients()) == 0

    def test_makefile(self):
        if not sys.version_info[0] is 3:
            assert self.socket.makefile().default_bufsize == 8192
        else:
            assert self.socket.makefile()._CHUNK_SIZE == 8192

    def test_send_recv(self):
        self.socket.bind('127.0.0.1', 12345)
        self.new_socket.bind(port=8000)  # Binds to 127.0.0.1:8000
        self.new_socket.connect('127.0.0.1', 12345)
        self.socket.recv()
        self.new_socket.send('hello')
        assert self.new_socket.send('hello') == len('hello')
        assert self.socket.recv() == 'hello'

    def test_send_recv(self):
        self.socket.bind('127.0.0.1', 12345)
        self.new_socket.bind(port=8000)  # Binds to 127.0.0.1:8000
        self.new_socket.connect('127.0.0.1', 12345)
        self.socket.recv()
        self.new_socket.send('\x87\x88\x89')
        assert self.socket.recv() == '\x87\x88\x89'

    def test_send_recv_chunks(self):
        self.socket.bind('127.0.0.1', 12345)
        self.new_socket.bind(port=8000)  # Binds to 127.0.0.1:8000
        self.new_socket.connect('127.0.0.1', 12345)
        self.socket.recv()
        assert self.new_socket.send('hello' * 20000) == len('hello') * 20000
        assert len(self.socket.recv()) == len('hello') * 20000

    def test_set_ip(self):
        self.socket.bind('127.0.0.1', 12345)
        assert self.socket.get_ip() == '127.0.0.1'
        self.socket.set_ip('0.0.0.0')
        assert self.socket.get_ip() == '0.0.0.0'

    def test_set_port(self):
        self.socket.bind('127.0.0.1', 12345)
        assert self.socket.get_port() == 12345
        self.socket.set_port(8000)
        assert self.socket.get_port() == 8000

    def test_set_timeout(self):
        self.socket.settimeout(1)
        assert self.socket.gettimeout() == 1

    def test_unbind(self):
        self.socket.bind('127.0.0.1', 12345)
        assert self.socket.is_binded() == True
        self.socket.unbind()
        assert self.socket.is_binded() == False

class Test_Server_Client(unittest.TestCase):

    def setUp(self):
        self.server = pysocket.Server(('', 8001))  # Starts a threaded server on 127.0.0.1:8001
        self.client = pysocket.Client(('', 8002), ('', 8001))  # Starts a client on 127.0.0.1:8002
        self.client2 = pysocket.Client(('', 8003), ('', 8001))  # Starts another client on 127.0.0.1:8003

        # Start serving
        self.server.serve()

    def tearDown(self):
        self.server.quit()
        self.client.quit()
        self.client2.quit()

    def test_all(self):
        assert self.client.send('hello') == 5
        assert self.client2.recv() == 'hello'  # Server should send data to client2

if __name__ == '__main__':
    unittest.main()
