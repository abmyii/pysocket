import socket as _socket
import zlib as _zlib
import time as _time
import sys as _sys
import threading as _threading


class SocketError(Exception):
    pass


class socket():

    """Base class which replaces socket.socket"""
    
    def __init__(self, family=2, type=2, proto=0, _sock=None, ip=None, port=None, timeout=0.5, thread=False):
        """Makes a new socket"""
        self._always_accept = False
        self._socket = _socket.socket(family, type, proto, _sock)
        self._socket_fam = family
        self._socket_type = type
        self._socket_proto = proto
        self._socket_sock = _sock
        self._blocked = []
        self._clients = []
        self._is_server = False
        self._max_recv = 65535
        self._max_send = 65535
        self._binded = False
        self._connected = False
        self._timeout = timeout
        self._packets = {'disconnect': '*<disconnect>*', '-disconnect-': '*<-disconnect->*',
                         'sending': '*<sending data>*', 'sent': '*<sent data>*', 'connect': '*<-connect->*'}
        self._timers = []
        self._stop_recv = False
        self._recv_started = False
        self._threaded_recvs = []
        self._thread = thread
        self._history = []

        # Set socket timeout and options
        self._socket.settimeout(self._timeout)
        self._socket.setsockopt(1, 6, 1)

        # Bind socket if ip and port are valid otherwise keep unbinded
        self._ip = ip or '0.0.0.0'
        self._port = port or 0
        self.bind(ip, port)

    def __reinit__(self):
        """Re-inits the socket. Good for when we want to start from fresh"""
        self._socket.close()
        self._socket = _socket.socket(self._socket_fam, self._socket_type, self._socket_proto, self._socket_sock)

        # Update now-changed values
        self._is_server = False
        self._binded = False
        self._connected = False
        
        # Set socket timeout and options
        self._socket.settimeout(self._timeout)
        self._socket.setsockopt(1, 6, 1)

    def _catch_exceptions(self, error):
        """Shortcut so we don't have to paste the below code everywhere"""
        if error.args[0] is "timed out":
            pass  # "Timed out" is not a real exception, so we can just leave this out
        elif error.args[0] is 22:
            raise SocketError("[Errno 22] Invalid argument. Socket has probably not been binded.")
        elif error.args[0] is 95:
            raise SocketError("[Errno 95] Operation not supported.")
        elif error.args[0] is 107:
            raise SocketError("[Errno 107] Transport endpoint is not connected.")
        elif error.args[0] is 111:
            pass  # "Connection refused" is also not a real exception

    def _compress(self, string, level=6):
        # py2k
        if _sys.version_info[0] is 2:
            return bytearray(_zlib.compress(_zlib.compress(string, level), level))
        
        # py3k
        data = bytes(string, 'latin-1')
        return bytearray(_zlib.compress(_zlib.compress(data, level), level))

    def _decompress(self, string, level=6):
        # py2k
        if _sys.version_info[0] is 2:
            return _zlib.decompress(_zlib.decompress(buffer(string)))
        
        # py3k
        return _zlib.decompress(_zlib.decompress(string)).decode('latin-1')
    
    def _send(self, send, data, sendto):
        try:
            if sendto:
                send(data, sendto)
            else:
                send(data)
        except Exception as error:
            self._catch_exceptions(error)

    def accept(self, blocking=False):
        """Accepts client connection request"""

        # Block
        if blocking:
            self._socket.settimeout(None)
        
        try:
            conn, addr = self._socket.accept()

            # If the client ip isn't in the blocked list, then we add it to the clients list
            if not addr[0] in self._blocked:
                self.onAccept(addr)
                self._clients.append((addr[0], addr[1]))

            if blocking:
                # Unblock
                self._socket.settimeout(self._timeout)
                
                # Like socket.accept
                return conn, addr
                
        except Exception as error:
            if self._binded and error.args[0] is "timed out":
                # accept() is not supposed to time out, so we thread it
                if self.thread:
                    _threading.Thread(target=self.accept).run()
            else:
                self._catch_exceptions(error)

        # If self._always_accept is true, then regardless, rerun this function
        if self._always_accept:
            _threading.Thread(target=self.accept).run()

    def accept_all(self, MAX=100):
        """Allows socket to accept all connections"""
        self.listen(MAX)
        self._always_accept = True
        self.accept()  # Start the threading loop

    def add_blocked(self, ip):
        """Blocks given IP"""
        self._blocked.append(ip)

    def bind(self, addr='127.0.0.1', port=8000):
        """Binds ip and port to socket"""
        self.__reinit__()  # Reinit socket, because binding a socket which has already been binded/closed raises an error

        # Bind socket
        try:
            self._socket.bind((addr, port))
            self._ip = addr
            self._port = port
        except TypeError:
            if not addr:
                return
            # Compatiblity for socket.bind
            self._socket.bind(addr)
            self._ip = addr[0]
            self._port = addr[1]

        self._is_server = True
        self._binded = True

        if self._thread:
            # Start reciving thread
            _threading.Timer(0.45, self.recv, args=(0, 0, 1)).start()

    def close(self):
        """Closes socket"""
        self.stop_threads()  # Stops all of the threads
        self._socket.close()

    def connect(self, addr, port=None, ex=False):
        """Connect to another socket"""
        if ex:
            try:
                self._socket.connect_ex((addr, port))
            except TypeError:
                self._socket.connect_ex(addr)
        else:
            try:
                self._socket.connect((addr, port))
            except TypeError:
                self._socket.connect(addr)
        self.send(self._packets['connect'])
        self._is_server = False
        self._connected = True

        if self._thread:
            # Start reciving thread
            _threading.Timer(0.45, self.recv, args=(0, 0, 1)).start()

    def disconnect_all(self):
        """Disconnects all clients"""
        # Tell all clients to disconnect
        for client in self._clients:
            self.sendto(self._packets['disconnect'], client[0], client[1])

        # Clear all clients
        self._clients = []

    def disconnect_client(self, client_ip, client_port):
        """Disconnects a client"""
        for client in self._clients:
            if client_ip is client[0] and client_port is client[1]:
                self.sendto(self._packets['disconnect'], client_ip, client_port)
                del self._clients[self._clients.index(client)]
                break

    def dup(self):
        """Returns duplicate of current socket, without ip and port, because of binding conflict issuses"""
        return socket(self._socket_fam, self._socket_type, self._socket_proto, self._socket_sock, timeout=self._timeout)

    def get_client(self, ip, port=None):
        for client in self._clients:
            if ip in client[0]:
                if port:
                    if port is client[1]:
                        return (ip, port)
                else:
                    return (ip, client[1])

    def get_ip(self):
        """Gets ip"""
        return self._ip
    
    def get_port(self):
        """Gets port"""
        return self._port

    def getclients(self):
        """Returns a dict of all clients"""
        return self._clients

    def gethistory(self, amount=None):
        if not amount:
            return self._history
        return self.history[-amount]

    def getpeerinfo(self):
        """Gets peer info"""
        if not self._is_server:
            return self._socket.getpeername()

    def getsockname(self, _tosend=False):
        if _tosend:
            return self._ip + ', ' + str(self._port)
        else:
            return (self._ip, self._port)

    def getsockopt(self, *args):
        return self._socket.getsockopt(*args)

    def gettimeout(self):
        return self._timeout

    def is_binded(self):
        """Returns if socket is binded"""
        return self._binded

    def leave(self):
        """If socket is connected to a server, disconnects socket from server"""
        if self._connected is True:
            self.send(self._packets['-disconnect-'])
            self._connected = False
        if self._binded:
            self._is_server = True
        self.__reinit__()  # Restart socket

    def listen(self, max):
        self._socket.listen(max)

    def makefile(self, mode='r', bufsize=-1):
        return self._socket.makefile(mode, bufsize)

    def onAccept(self, addr):
        "Reimplement this function in your own subclass"
        pass

    def onConnect(self, addr):
        "Reimplement this function in your own subclass"
        pass

    def recv(self, buffersize=False, _ip=False, _isthread=False):
        """Recives data that has been sent from another socket and processes it"""

        if not buffersize:
            buffersize = self._max_recv

        # Nested functions for processing the recived data
        def recvall(ip):
            """Recives all the chunks of data from the sending socket, and then returns the data"""
            data = ''

            # Recive all chunks of data and store in the data str
            while True:

                recv = self._decompress(self._socket.recv(buffersize))

                if recv == self._packets['sent']:  # 'is' comparison fails
                    break

                data += recv

            return data

        def rem_client(addr):
            """Removes a client from the self._clients dict"""
            for client in self._clients:
                if addr[0] == client[0] and addr[1] == client[1]:
                    del self._clients[self._clients.index(addr)]
                    return ''

        def conn_client(ip):
            """Adds a client to the self._clients dict"""
            self.onConnect(ip)
            self._clients.append(ip)
            return ''

        if _isthread:
            # Restart recv
            _threading.Timer(0.45, self.recv, args=(0, 0, 1)).start()

        if self._binded:
            try:
                data = self._socket.recv(buffersize)
                try:
                    ip = self._decompress(data).split(',')
                    ip = (ip[0], int(ip[1]))
                except:
                    if self._decompress(data) in self._packets.values():
                        # Probably called too late to get ip. Just break
                        return ''
                    else:
                        # Probably normal socket sent data
                        return data
                
                data = self._decompress(self._socket.recv(buffersize))
               
                if data in self._packets.values():
                    # Rename just for clarity
                    packet = data

                    # Make switch dict, check packets & work accordingly
                    switch_dict = {self._packets['disconnect']: self.__reinit__, self._packets['-disconnect-']: rem_client,
                                   self._packets['connect']: conn_client, self._packets['sending']: recvall}
                    try: data = switch_dict.get(packet)(ip)
                    except: switch_dict.get(packet)(); data = ''

                if data:
                    self._history.append([ip, data])

                # Return data
                if not _isthread:
                    if not _ip:
                        return data
                    else:
                        return (ip, data)
                else:
                    if not _ip:
                        if not data is '' and not data is u'':
                            self._threaded_recvs.append(data)
                    else:
                        self._threaded_recvs.append((ip, data))
                    return ''

            except Exception as error:
                self._catch_exceptions(error)
                return ''  # Because socket timed out, return a string

        raise SocketError("Socket has not been binded. Bind before reciving.")

    def recvfrom(self, buffersize=None):
        if buffersize == None:
            buffersize = self._max_recv

        try:
            ip, recv = self.recv(buffersize, _ip=True)
            return (recv, ip)
        except ValueError:
            return ''

    def recvinto(self, buf):
        recv = self.recv()
        buf.write(recv)
        return len(recv)

    def send(self, data, oldsock=False, _send=None, _sendto=None, ip=False):
        """Sends data over socket. If oldsock is true, sends without processing data"""
        olddata = data

        if oldsock:
            self._send(_send, data, _sendto)
            return len(olddata)
        
        if _send == None:
            _send = self._socket.send
        
        # Compress data
        data = self._compress(data)

        # Send data
        self._send(_send, self._compress(self.getsockname(_tosend=True)), _sendto)
        if not olddata in self._packets.values() and not ip:
            self._send(_send, self._compress(self._packets['sending']), _sendto)
        
        if len(data) < self._max_send:
            self._send(_send, data, _sendto)
        else:
            chunk = 0
            
            # Send all chunks of data
            while True:
                if len(data[chunk:]) > self._max_send:
                    self._send(_send, data[chunk:chunk + self._max_send], _sendto)
                    chunk += self._max_send
                else:
                    self._send(_send, data[chunk:], _sendto)
                    break

        if not olddata in self._packets.values() and not ip:
            self._send(_send, self._compress(self._packets['sent']), _sendto)

        return len(olddata)
    
    def sendall(self, data, _send=None, _sendto=None):
        # Turn data to bytes if python version is py3k
        data = self._tobytes(data)
        
        # If the data is a packet then just use the send function. Otherwise continue below
        if data in self._packets.values():
            self._send(_send, data, _sendto)

        if _send == None:
            _send = self._socket.send
        
        # Compress data
        data = self._compress(data)
        
        # Send data
        self._send(_send, self._compress(self.getsockname(_tosend=True)), _sendto)
        self._send(_send, self._compress(self._packets['sending']), _sendto)
        
        for d in data:
            self._socket.send(d)
            
        self._send(_send, self._compress(self._packets['sent']), _sendto)
        
        return len(data)

    def sendto(self, data, addr, port=None):
        if port:
            self.send(data, _send=self._socket.sendto, _sendto=(addr, port))
        else:
            self.send(data, _send=self._socket.sendto, _sendto=addr)

    def sendtoall(self, data):
        for client in self.getclients():
            self.sendto(data, client)

    def set_ip(self, ip):
        """(Re-)binds the socket with given ip"""
        self.bind(ip, self._port)

    def set_max_acceptions(self, MAX):
        """Sets max allowed connections"""
        self._socket.listen(MAX)

    def set_port(self, port):
        """(Re-)binds the socket with given port"""
        self.bind(self._ip, port)

    def set_socket_fam(self, family):
        """Remakes the socket with given family"""
        self._socket = _socket.socket(family, self._socket_type, self._socket_proto, self._socket_sock)
        self._socket_fam = family

    def set_socket_proto(self, proto):
        """Remakes the socket with given proto"""
        self._socket = _socket.socket(self._socket_fam, self._socket_type, proto, self._socket_sock)
        self._socket_proto = proto

    def set_socket_sock(self, sock):
        """Remakes the socket with given sock"""
        self._socket = _socket.socket(self._socket_fam, self._socket_type, self._socket_proto, sock)
        self._socket_sock = sock

    def set_socket_type(self, type):
        """Remakes the socket with given type"""
        self._socket = _socket.socket(self._socket_fam, type, self._socket_proto, self._socket_sock)
        self._socket_type = type

    def settimeout(self, timeout):
        """Sets socket timeout"""
        self._timeout = timeout
        self._socket.settimeout(timeout)

    def setsockopt(self, level, option, value):
        self._socket.setsockopt(level, option, value)

    def stop_threads(self):
        """If all threads"""
        self._always_accept = False
        self._stop_recv = True
        self._recv_started = False

    def threaded_recvs(self):
        """Returns data recived by the threads"""
        return self._threaded_recvs

    def type(self):
        return self._socket_type

    def unbind(self):
        """Unbinds socket"""
        self.__reinit__()


class Server(socket):

    """Server class which can be sub-classed"""

    def __init__(self, addr, thread=True, _timeout=0.5):
        socket.__init__(self, timeout=_timeout)
        self.bind(addr[0], addr[1])
        self._thread = thread

    def sendtoall(self, data, _ip=None):
        for client in self.getclients():
            if _ip:
                if not client[1] is _ip[1]:
                    self.sendto(data, client[0], client[1])
            else:
                self.sendto(data, client[0], client[1])

    def setthread(self, true_false):
        self._thread = true_false

    def serve(self, _retdata=False, _rettoall=True):
        """Simple serving function"""

        if self._thread:
            _threading.Timer(0.1, self.serve).start()
        
        try:
            data, ip = self.recvfrom()
            if _rettoall:
                if not data is '':
                    self.sendtoall(data, ip)
                    if _retdata:
                        return (ip, data)
        except:
            pass

    def quit(self):
        """Quits server after disconnecting all clients"""
        self.disconnect_all()
        self.close()
        self._thread = False


class Client(socket):

    """Client class which can be sub-classed"""

    def __init__(self, addr, server, _timeout=0.5):
        socket.__init__(self, timeout=_timeout)
        self.bind(addr[0], addr[1])
        self.connect(server[0], server[1])  

    def proc_recv(self, func):
        """Threaded function to recive data and call *func* with the data as the arg"""
        self.recv(_isthread=True)
        for data in self.threaded_recvs():
            func(data)  # Call the function with data as the arg
        _threading.Timer(0.5, target=self.proc_recv, args=(func))  # Thread function

    def quit(self):
        """Quits server after disconnecting all clients"""
        self.leave()
        self.close()
