import socket
import time
import db_access
import threading
import os
import select
import ntplib


SERVER_IP  = "10.0.3.10"
UDP_PORT = 5000
hostname = socket.gethostname()
localIP = socket.gethostbyname(hostname)

#db_conn = db_access.create_connection("database/db_peer.db")

local_ID = -1
off_flag = 0

			#DATAGRAMA HELLO
#	|	ID	|	RAZAO(0)	|	TIMESTAMP 
def send_hello_packet (socket_UDP):
	razao = 0
	timestamp = time.time_ns()
	hello = (str(local_ID) +"/"+ str(razao)+"/"+ str(timestamp)).encode()
	socket_UDP.sendto(hello,(SERVER_IP,UDP_PORT))

			#DATAGRAMA GOODBYE
#	|	IP	|	RAZAO(1)	|	TIMESTAMP 
def send_goodbye_packet (socket_UDP):
	razao = 1
	timestamp = time.time_ns()
	gbye = (str(local_ID) +"/"+str(razao)+"/"+ str(timestamp)).encode()
	socket_UDP.sendto(gbye,(SERVER_IP,UDP_PORT))

			#DATAGRAMA ERROR
#	|	IP	|	RAZAO(2)	|	TIMESTAMP 
def error_packet (socket_UDP):
	socket_UDP.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
	localIP=socket.gethostbyname(socket.gethostname())
	razao = 2
	timestamp = time.time()
	hello = (str(local_ID) + str(razao)+ str(timestamp)).encode()
	socket_UDP.sendto(hello,(MCAST_IP,MCAST_PORT))		


def send_test_packet(socket ,peer_ip):
	global local_ID
	timestamp = time.time_ns()
	message = (str(local_ID)+"/"+"3"+"/"+str(timestamp)).encode()
	socket.sendto(message, (peer_ip, UDP_PORT))


def test_routes_directly(socket):
	ntp_sync()
	db_conn = db_access.create_connection("database/db_%s.db" % hostname)
	ip_list = db_access.get_all_routes_destinations(db_conn)
	db_conn.close()
	for ip in ip_list:
		send_test_packet(socket, ip[0])	
		pass

def ask_cost(socket, ip, destination):
	global local_ID
	message = (str(local_ID)+"/"+"4"+"/"+destination).encode()
	socket.sendto(message,(ip,UDP_PORT))

def ask_neighbours_for_cost(socket):
	db_conn = db_access.create_connection("database/db_%s.db" % hostname)
	ip_list = db_access.get_all_routes_destinations(db_conn)
	db_conn.close()
	for ip in ip_list:
		for ip_neighbours in ip_list:
			if(ip[0] != ip_neighbours[0]):
				ask_cost(socket, ip_neighbours[0], ip[0])	
			pass	
	
def ntp_sync():
	ntp_pool = '1.pt.pool.ntp.org'
	call = ntplib.NTPClient()
	response = call.request(ntp_pool, version=3)
	try:
		t=response.orig_time
		local_time = time.time()
		time_difference=local_time-t
		#print("Time difference ",time_difference)
		time.sleep(time_difference)

	except Exception as e :
		print("Error getting ntp_sync: %s" % e)



def receive_packet(socket, message, peer_ip, recv_timestamp):
	db_conn = db_access.create_connection("database/db_%s.db" % hostname)
	global local_ID
	message_fields = message.split("/")
	sender_id = message_fields[0]
	m_type = message_fields[1]

# -> Hello Message  | id | m_type | new self id | neighbours by server |		
	if m_type == "0":
		if sender_id == "0":
			# -> Hello Message from Server
			local_ID = int(message_fields[2])
			for ip in message_fields[3:]:
				#new neighbour
				if ip != localIP:
					route = (local_ID, ip, ip, 999999)
					db_access.insert_route(db_conn, route,0)
			print("Stored -> ", *message_fields[3:])
			return 0
		else:
			print("Received hello packet not from server")
			return 1
		db_conn.close()
# -> Goodbye Message  | id | m_type | IP_peer |		
	elif m_type == "1":
		if sender_id == "0":
			if db_access.delete_route_by_destination(db_conn, message_fields[2]) == 0:
				print("Deleted "+message_fields[2]+" from table")
			else:
				print("Error deleting route") 
			dest_list = db_access.get_destinations_by_next_hop(db_conn, message_fields[2]) 
			if dest_list != None and dest_list != 1 :
				for ip in dest_list:
					send_test_packet(socket, ip)
			else:
				print("Error fething destinations (Goodbye message)")
			return 0
		else:
			print("Goodbye message from peer, removing from possible routes")
			if(db_access.delete_route(db_conn, int(sender_id)) == 0):
				
				print("Deleted successfully route to %s" % peer_ip)
			else:
				print ("Route deletetion failed")
		db_conn.close()

# -> Error  | id | m_type | error code | free field |
	elif m_type == "2":
		error_code = message_fields[2]
		if sender_id == "0":
			print("Error type %s" % error_code) 
		else:
			print ("Error received from peer %s" % error_code)

# -> Test Message  | id | m_type | timestamp_saida | null/End-to-End_result |			
	elif m_type == "3":
		#print("SENT message at %d " % int(message_fields[2]))
		wayback_result = recv_timestamp-int(message_fields[2])
		#print("Received test message, current time elapsed on coming trip (End-to-End) = %s s" % str(wayback_result))  

		if len(message_fields) == 4:
			test_result = int(message_fields[3])
			route = (local_ID, peer_ip, peer_ip, test_result)
			if message_fields[2] != "-1":
				db_access.insert_route(db_conn, route, 0)
				time_left = time.time_ns()
				response = (str(local_ID)+"/"+"3"+"/"+"-1"+"/"+str(wayback_result)).encode()
				socket.sendto(response,(peer_ip,UDP_PORT))
			else:
				db_access.insert_route(db_conn, route, 1)
			return 0
		else : 
			#envia result e timestamp
			time_left = time.time_ns()
			message = (str(local_ID)+"/"+"3"+"/"+str(time_left)+"/"+str(wayback_result)).encode()
			socket.sendto(message,(peer_ip,UDP_PORT))
			return 0
		db_conn.close()

# -> Request Cost Message  | id | m_type | destination_ip | null/cost |	
	elif m_type == "4":
		ip_destino = message_fields[2]
		if len(message_fields) < 4:
			cost = db_access.check_cost_from_destination(db_conn, ip_destino)
			if cost != 1:
				response = (str(local_ID)+"/"+"4"+"/"+ip_destino+"/"+str(cost)).encode()
				socket.sendto(response,(peer_ip,UDP_PORT))
				return 0
			else:
				return 1
		else:	
			cost = int(message_fields[3])+db_access.check_cost_from_destination(db_conn, peer_ip)
			route = (local_ID, ip_destino, peer_ip, cost)
			db_access.insert_route(db_conn, route,1)
			return 0	
		db_conn.close()		


def udp_socket_listen(socket):
	#> threading
	global off_flag
	active_threads = []
	try:
		while off_flag == 0:
			r,_,_ = select.select([socket],[],[], 0)
			if r :
				message_recv,(peer_ip, peer_port) = socket.recvfrom(1024)			
				recv_timestamp = time.time_ns()
				# print("RECEIVED message at %d " % recv_timestamp)
				# print("Received response : %s" % message_recv.decode() )
				t2 = threading.Thread(target = receive_packet, args = (socket, message_recv.decode(), peer_ip, recv_timestamp,))
				t2.start()
				active_threads.append(t2)
		
		return
		for thread in active_threads:
			thread.join()
		
	except Exception as e:
		print(e) 

def boot_up(time_between_tests):
	global off_flag
	table_count = 0

	socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socket_UDP.bind((localIP,int(UDP_PORT)))
	t1 = threading.Thread(target=udp_socket_listen, args=(socket_UDP,))
	t1.start()

	while table_count == 0:
		send_hello_packet(socket_UDP)
		time.sleep(10)
		db_conn = db_access.create_connection("database/db_%s.db" % hostname)
		table_count = db_access.count_routes(db_conn)
		db_conn.close()		
		pass
	
	while off_flag == 0:
		test_routes_directly(socket_UDP)
		ask_neighbours_for_cost(socket_UDP)
		time.sleep(time_between_tests)

	t1.join()
	boot_off(socket_UDP)
	return

def boot_off(socket):
	send_goodbye_packet(socket)
	os.remove("database/db_%s.db" % hostname)
	print("Booting off...")


if __name__ == '__main__':
	db_conn = db_access.create_connection("database/db_%s.db" % hostname)
	if db_conn is not None:
		db_access.create_table(db_conn, db_access.create_peer_routes_table)
		db_conn.close()

		tester_thread = threading.Thread(target=boot_up, args=(30,))
		tester_thread.start()
		res = input("Send \"x\" to stop peer\n")
		if res == "x":
			 off_flag = 1

		tester_thread.join()
	
	else:
		print("Can't access table")
		
