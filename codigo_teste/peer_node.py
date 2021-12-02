import socket
import time
import db_access
from threading import Thread

MCAST_IP = '224.0.0.1'
MCAST_PORT = 5001
MULTICAST_TTL = 2
localIP=socket.gethostbyname(socket.gethostname())

			#DATAGRAMA HELLO
#	|	IP	|	RAZAO(0)	|	TIMESTAMP 
def hello_packet (socket_UDP):
	socket_UDP.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
	razao = 0
	timestamp = time.time()
	hello = (localIP + str(razao)+ str(timestamp)).encode()
	socket_UDP.sendto(hello,(MCAST_IP,MCAST_PORT))

			#DATAGRAMA GOODBYE
#	|	IP	|	RAZAO(1)	|	TIMESTAMP 
def goodbye_packet (socket_UDP):
	socket_UDP.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
	razao = 1
	timestamp = time.time()
	hello = (localIP + str(razao)+ str(timestamp)).encode()
	socket_UDP.sendto(hello,(MCAST_IP,MCAST_PORT))	

			#DATAGRAMA ERROR
#	|	IP	|	RAZAO(2)	|	TIMESTAMP 
def error_packet (socket_UDP):
	socket_UDP.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
	localIP=socket.gethostbyname(socket.gethostname())
	razao = 2
	timestamp = time.time()
	hello = (localIP + str(razao)+ str(timestamp)).encode()
	socket_UDP.sendto(hello,(MCAST_IP,MCAST_PORT))		





if __name__ == '__main__':
	socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	hello_packet(socket_UDP)
	print(localIP)
	socket_UDP.bind(("10.0.2.15",7777))

	while True:
		try:
			recv_data, (fromIP, ports) = socket_UDP.recvfrom(1024)
			print(recv_data)
			print(fromIP)
		except:
			print("error")


	goodbye_packet(socket_UDP)



	socket_UDP.close()