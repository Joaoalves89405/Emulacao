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
def send_hello_packet (socket_UDP):
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

def boot_up():
	#> Entering Overlay network
	#> send Hello packet
	#> receive response treat each one
	#> Case server > 
		#> Create database 
		#> Add peer0
	#> Case peer >
		#> Hold until DB is created
		#> add to DB

	socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socket_UDP.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
	send_hello_packet(socket_UDP)

	


	pass	


if __name__ == '__main__':
	
	goodbye_packet(socket_UDP)



	socket_UDP.close()