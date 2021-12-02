import socket 
from threading import Thread


serverIP = socket.gethostbyname(socket.gethostname())
MCAST_IP = '224.0.0.1'
MCAST_PORT = 5001



if __name__ == '__main__':

	socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	socket_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	print(serverIP)
	socket_UDP.bind((MCAST_IP,MCAST_PORT))
	i=0

	while i == 0:
		try:
			recv_data, (fromIP, ports) = socket_UDP.recvfrom(1024)
			print(recv_data.decode())
			print(fromIP)
		except:
			print("error")
			socket_UDP.close()
			i=1
