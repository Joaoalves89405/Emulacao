import socket
import time
import db_access
from threading import Thread



SERVER_IP  = "127.0.1.1"
UDP_PORT = 5001
localIP = socket.gethostbyname(socket.gethostname())
#db_conn = create_connection("database/db_%s.db" % hostname)
db_conn = db_access.create_connection("database/db_peer.db")

local_ID = -1

			#DATAGRAMA HELLO
#	|	ID	|	RAZAO(0)	|	TIMESTAMP 
def send_hello_packet (socket_UDP):
	razao = 0
	timestamp = time.time()
	hello = (str(local_ID) +"/"+ str(razao)+"/"+ str(timestamp)).encode()
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


def receive_packet(message, peer_ip):
	message_fields = message.split("/")

	if message_fields[1] == "0":
		if message_fields[0] == "0":
			# -> Hello Message from Server
			local_ID = int(message_fields[2])
			for ip in message_fields[3:]:
				#new neighbour
				route = (local_ID, ip, ip, 999999)
				db_access.insert_route(db_conn, route)
			print("Inserted all neighbours on the database")
			return 0
		else:
			print("Received hello packet not from server")
	else:
		print("Message receive not Hello Packet")



def udp_socket_listen(socket):
	#> threading
	try:
		while True:
			message_recv,(peer_ip, peer_port) = socket.recvfrom(1024)
			if(message_recv != None):
				print("Received response : %s" % message_recv.decode() )
				response = receive_packet(message_recv.decode(), peer_ip)
				if response == 0:
					return
	except Exception as e:
		print(e) 


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
	udp_socket_listen(socket_UDP)

if __name__ == '__main__':
	
	if db_conn is not None:
		db_access.create_table(db_conn, db_access.create_peer_routes_table)
	else:
		print("Can't access table")
	boot_up()