import socket
import time
import db_access
from threading import Thread



SERVER_IP  = "127.0.1.1"
UDP_PORT = 5001
localIP = socket.gethostbyname(socket.gethostname())

			#DATAGRAMA HELLO
#	|	ID	|	RAZAO(0)	|	TIMESTAMP 
def send_hello_packet (socket_UDP):
	razao = 0
	timestamp = time.time()
	hello = (localIP +"/"+ str(razao)+"/"+ str(timestamp)).encode()
	socket_UDP.sendto(hello,(SERVER_IP,UDP_PORT))

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
	socket_UDP.bind((localIP,5000))
	send_hello_packet(socket_UDP)

if __name__ == '__main__':
	
	boot_up()