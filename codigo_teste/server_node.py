import socket 
from db_access import * 
from threading import Thread

hostname = socket.gethostname()
serverIP = socket.gethostbyname(hostname)
UDP_PORT = 5001

Server_ID = "0"

db_conn = create_connection("database/db_%s.db" % hostname)



def respond_message(message, peer_ip):
	message_fields = message.split("/")
	
				#HELLO MESAGE
	if (message_fields[1] == "0"):
			#estado | area | IP
		peer = (1,None,peer_ip)
		if(insert_peer(db_conn, peer) == 0):
			print("Succefully added peer")

			ips_data = ""
			ip_list = get_allpeer_ip(db_conn)

			for idx,tuple in enumerate(ip_list):
				ips_data = ips_data+"/"+tuple[0]

			peer_id = get_peerID(db_conn, peer_ip)
			#   SERVER_ID	.|	TPM		.|	GIVEN_ID	.| 	NEIGHBOUR_IP /  NEIGHBOUR_IP	|
			response = Server_ID+"/"+"0"+"/"+str(peer_id)+ips_data
			print("Responde hello packet: %s" % response)
			return response
		else:
			print("Error inserting peer")

				#GOODBYE MESSAGE
	elif(message_fields[1] == "1"):
		if(set_peer_state(db_conn,peer_ip,0) == 0 & delete_route_by_destination(db_conn,peer_ip) == 0):
				print("Removed Peer")	
		 #remover entradas restantes desse peer na tabela dos outros peers
				

			#ERROR MESSAGE
	elif(message_fields[1] == "2"):
		pass



		
		
def udp_socket_listen():
	socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	socket_UDP.bind((serverIP,UDP_PORT))

	try:
		while True:
			message_recv,(peer_ip, peer_port) = socket_UDP.recvfrom(1024)
			if( message_recv != None):
				#> threading
				response = respond_message(message_recv.decode(), peer_ip)
				socket_UDP.sendto(response.encode(),(peer_ip,peer_port))

	except Exception as e:
		print(e)
		socket_UDP.close()
		return
	


	

if __name__ == '__main__':
	
	print(serverIP)
	if db_conn is not None:
		create_table(db_conn, create_server_tables)
	else:
		print("Can't access table")

	udp_socket_listen()