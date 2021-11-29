import socket
import time
import db_access
from threading import Thread


serverIP = socket.gethostbyname(socket.gethostname())
MCAST_IP = '224.0.0.1'
MCAST_PORT = 5001
MULTICAST_TTL = 2


def broadcast_Message( message):
	socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socket_UDP.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

	timestamp = time.time()
	udp_data = (message + str(timestamp)).encode()

	socket_UDP.sendto(udp_data, (MCAST_IP,MCAST_PORT))



if __name__ == '__main__':

	for x in range(5):
		val = input('Enter message to send:')
		broadcast_Message(str(val))
		pass

	socket_UDP.close()