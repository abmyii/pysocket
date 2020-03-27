import sys
sys.path.append('..')
import pysocket

class Socket(pysocket.socket):
    def onConnect(self, addr):
        print(addr)

sock = Socket()
sock.bind()

print('Serving on %s:8000' % sock.get_ip())

while True:
    recv = sock.recvfrom()
    if recv and recv[0]:
        print(sock.getclients())
        print(recv[1][0] + ':' + str(recv[1][1]) + ' said: ' + recv[0])
        sock.sendto('Recived your message (%s)' % (recv[0]), recv[1])
