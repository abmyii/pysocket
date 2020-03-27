import sys
sys.path.append('..')
import pysocket, random

sock = pysocket.socket()
sock.bind(port=random.randint(1025, 7999))
port = sock.get_port()

server_ip = input('Server IP: ')
server_port = 8000
sock.connect(server_ip, server_port)

while True:
    text = input('You say: ')
    sock.sendto(text, (server_ip, server_port))
    recv = sock.recv()
    if recv:
        print('Server said: ' + recv)
