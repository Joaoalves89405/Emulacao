import socket
import time
import db_access
import threading
import os
import select
import ntplib
import random
import base64


SERVER_IP  = "10.0.3.10"
UDP_PORT = 5000
APP_PORT_R = 9000
APP_PORT_S = 9090
hostname = socket.gethostname()
localIP = socket.gethostbyname(hostname)
BUFF_SIZE = 65536
db_dir = "codigo_teste/database/db_%s.db" % hostname

ntp_sync_count = 0
latency = 0
packets = 0

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

def	send_encapsulated_message(socket, data, destination):
	global local_ID
	global ntp_sync_count
	db_conn = db_access.create_connection(db_dir)
	next_hop = db_access.next_hop_by_destination(db_conn, destination)
	#print("Manda pacote encapsulado para: "), print(next_hop)
	#print("Para o destino : "), print(destination) 
	db_conn.close()
	if ntp_sync_count == 25:
		ntp_sync()
		ntp_sync_count = 0
	ntp_sync_count+=1

	time_latency = time.time_ns()
	message = (str(local_ID)+"/5/"+data+"/"+str(localIP)+"/"+destination+"/"+str(time_latency)).encode()
	#print("//////MESNAGEM ENVIADA\n ", message, "\n")
	socket.sendto(message, (str(next_hop), UDP_PORT))	

def output_to_app(socket, data):
	#print(data.encode())
	socket.sendto(data.encode(), (localIP, APP_PORT_S))


def test_routes(socket):
	ntp_sync()
	db_conn = db_access.create_connection(db_dir)
	ip_list = db_access.get_all_routes_destinations(db_conn)

	#print("IP_LIST ", ip_list)
	
	# if network == "underlay":
	# 	for ip in [i for i in ip_list if i != None]:
	# 		print("testou uma rota da underlay"),print(ip[0])
	# 		send_test_packet(socket, ip[0])	
	# elif network == "overlay":
	for ip in [i for i in ip_list if i != None]:
			#print("testou na OVERLAY uma rota para: "),print(ip[0])
			next_hop = db_access.next_hop_by_destination(db_conn, ip[0])
			timestamp = time.time_ns()
			message = str(local_ID)+"|"+"3"+"|"+str(timestamp)+"|"+next_hop
			send_encapsulated_message(socket, message, ip[0])
	db_conn.close()


def ask_cost(socket, ip, destination):
	global local_ID
	message = (str(local_ID)+"/"+"4"+"/"+destination).encode()
	socket.sendto(message,(ip,UDP_PORT))

def ask_neighbours_for_cost(socket, ip_list):
	db_conn = db_access.create_connection(db_dir)
	db_list = db_access.get_all_routes_destinations(db_conn)
	#print("DB list: "), print(db_list)
	db_conn.close()
	for ip in db_list:
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
		print("NTP sync try again ")

def set_neighbours_peers(db_conn):
	peer_list = db_access.get_all_routes_destinations(db_conn)
	# for ip in db_list:
	# 	peer_list.append(ip[0])
	# 	pass
	#print("Lista de destinos"),print(peer_list)
	n_destinos = len(peer_list)+1
	if n_destinos<=2:
		rand_peer = random.sample(peer_list,1)	
	elif 2<n_destinos<=5:
		rand_peer = random.sample(peer_list,2)
	elif 5<n_destinos<=10:
		rand_peer = random.sample(peer_list,3)
	else:
		rand_peer = random.sample(peer_list,round(n_destinos*0.15))

	#print("Vizinhos do peer: %s" % rand_peer)
	return rand_peer

def rcv_test_message(socket, message_fields, recv_timestamp, source):
	wayback_result = recv_timestamp-int(message_fields[2])
	db_conn = db_access.create_connection(db_dir)
	#print("Received test from "+ peer_ip)
	#print("current time elapsed on coming trip (End-to-End) = "+str(wayback_result))  

	if len(message_fields) == 4:
		#mensagem inicial de teste
		used_nexthop = message_fields[3]
		try:
			planned_nexthop = db_access.next_hop_by_destination(db_conn, source)
		except Exception as e:
			print("Still don't have path to "+ str(source))
			return 0
		
		db_conn.close()
		#print("PLANNED NEXTHOP: "+str(planned_nexthop)+ " to "+ str(source))
		time_sent = time.time_ns()
		message = str(local_ID)+"|"+"3"+"|"+str(time_sent)+"|"+used_nexthop+"|"+planned_nexthop+"|"+str(wayback_result)
		send_encapsulated_message(socket, message, source)
		return 0

	elif len(message_fields) == 5:
		# mensagem de resposta final
		planned_nexthop = message_fields[3]
		e2e_result = message_fields[4]
		route = (local_ID, source, planned_nexthop, e2e_result)
		if localIP == planned_nexthop:
			pass
			#print("ADICIONADO PROPRIO COMO NEXTHOP NA ULTIMA MENSAGEM DE TESTE")
		else:
			db_access.insert_route(db_conn, route, 0)
		db_conn.close()
		return 0
		

	elif len(message_fields) == 6:
		# mensagem de resposta ao teste
		used_nexthop = message_fields[3]
		planned_nexthop = message_fields[4]
		e2e_result = message_fields[5]
		route = (local_ID, source, used_nexthop, e2e_result)
		if localIP == used_nexthop:
			pass
			#print("ADICIONADO PROPRIO COMO NEXTHOP")
		else:
			db_access.insert_route(db_conn, route, 0)
		db_conn.close()
		time_sent = time.time_ns()
		message = str(local_ID)+"|"+"3"+"|"+str(time_sent)+"|"+planned_nexthop+"|"+str(wayback_result)
		send_encapsulated_message(socket, message, source)
		return 0
	else:
	 	return -1

	# if len(message_fields) == 4:
	# 	test_result = int(message_fields[3])
	# 	time_left = time.time_ns()
	# 	if encap_flag:
	# 		route = (local_ID, localIP, source, test_result)
	# 		db_access.insert_route(db_conn, route, 0)
	# 		print("INSERTED ROUTE: ", end=' '),print(route)
	# 		response = str(local_ID)+"|"+"3"+"|"+"-1"+"|"+str(wayback_result)
	# 		#print("Rcv-encap_test-message from "),print(peer_ip)
	# 		send_encapsulated_message(socket, response, peer_ip)	
	# 	else:
	# 		route = (local_ID, peer_ip, peer_ip, test_result)
	# 		db_access.insert_route(db_conn, route, 0)
	# 		print("INSERTED ROUTE: ", end=' '),print(route)
	# 		response = (str(local_ID)+"/"+"3"+"/"+"-1"+"/"+str(wayback_result)).encode()
	# 		socket.sendto(response,(peer_ip,UDP_PORT))
	# else:
	# 	db_access.insert_route(db_conn, route, 1)
	# 	return 0
	# else : 
	# 	#envia result e timestamp
	# 	time_left = time.time_ns()
	# 	if encap_flag:
	# 		message = str(local_ID)+"|"+"3"+"|"+str(time_left)+"|"+str(wayback_result)+
	# 		#print("Rcv-test-message encapsulated but has no result from "),print(peer_ip)
	# 		send_encapsulated_message(socket, message, peer_ip)	
	# 	else:
	# 		message = (str(local_ID)+"/"+"3"+"/"+str(time_left)+"/"+str(wayback_result)).encode()
	# 		socket.sendto(message,(peer_ip,UDP_PORT))
	# 	return 0




def receive_packet(socket, message, peer_ip, recv_timestamp):
	db_conn = db_access.create_connection(db_dir)
	global local_ID
	global latency
	global packets
	message_fields = message.split("/")
	sender_id = message_fields[0]
	m_type = message_fields[1]


# -> Hello Message  | id | m_type | new self id | neighbours by server |		
	if m_type == "0":
		if sender_id == "0":
			# -> Hello Message from Server
			local_ID = int(message_fields[2])
			print(local_ID)
			for ip in message_fields[3:]:
				#new neighbour
				if ip != localIP:
					route = (local_ID, ip, ip, 922337203685477580)
					db_access.insert_route(db_conn, route,0)
			#print("Stored from server-> ", message_fields[3:])
			return 0
		else:
			new_peer = message_fields[2]
			route = (local_ID, new_peer, new_peer, 922337203685477580)
			if new_peer == localIP:
				pass
				#print("INSERE O PROPRIO REPETIDO")
			else:
				db_access.insert_route(db_conn, route,0)
			ip_list = set_neighbours_peers(db_conn)
			ask_neighbours_for_cost(socket, ip_list)
			#print("Stored new peer-> ", message_fields[2])
			#print("Received hello packet from new neighbour")
			return 0
		db_conn.close()

# -> Goodbye Message  | id | m_type | IP_peer |		
#	elif m_type == "1":
		# if sender_id == "0":
		# 	if db_access.delete_route_by_destination(db_conn, message_fields[2]) == 0:
		# 		print("Deleted "+message_fields[2]+" from table")
		# 	else:
		# 		print("Error deleting route") 
		# 	dest_list = db_access.get_destinations_by_next_hop(db_conn, message_fields[2]) 
		# 	if dest_list != None and dest_list != 1 :
		# 		for ip in dest_list:
		# 			#print("A testar para %s" % ip[0])
		# 			send_test_packet(socket, ip[0])
		# 			set_neighbours_peers(db_conn)
		# 	else:
		# 		print("Error fething destinations (Goodbye message)")
		# 	return 0
		# else:
		# 	print("Goodbye message from peer, removing from possible routes")
		# 	if(db_access.delete_route(db_conn, int(sender_id)) == 0):
				
		# 		print("Deleted successfully route to %s" % peer_ip)
		# 	else:
		# 		print ("Route deletetion failed")
		# db_conn.close()

# -> Error  | id | m_type | error code | free field |
	elif m_type == "2":
		error_code = message_fields[2]
		if sender_id == "0":
			print("Error type %s" % error_code) 
		else:
			print ("Error received from peer %s" % error_code)

# -> Test Message  	[ id | m_type | timestamp_saida | Next-Hop-IP ]	->
#					[ id | m_type | timestamp_saida | Next-Hop-IP 1 | Next-Hop-IP 2 | E2E res]	<-
#					[ id | m_type | timestamp_saida | Next-Hop-IP 2 | E2E result] ->		
#					
	elif m_type == "3":
		rcv_test_message(socket, message_fields, recv_timestamp, peer_ip )

# -> Request Cost Message  | id | m_type | destination_ip | null/cost |	
	elif m_type == "4":

		#-> set_neighbour_peers

		ip_destino = message_fields[2]
		if len(message_fields) < 4:
			try:
				cost = db_access.check_cost_from_destination(db_conn, ip_destino)
			except Exception as e:
				raise e
			response = (str(local_ID)+"/"+"4"+"/"+ip_destino+"/"+str(cost)).encode()
			socket.sendto(response,(peer_ip,UDP_PORT))
			return 0
		else:
			cost = int(message_fields[3])+int(db_access.check_cost_from_destination(db_conn, peer_ip))
			route = (local_ID, ip_destino, peer_ip, cost)
			#print(route)
			if peer_ip == localIP:
				pass
				#print("INSERIU PROPRIO QUANDO RECEBE")
			else:
				db_access.insert_route(db_conn, route,0)
				#print("INSERTED ROUTE: ", route)
			return 0	
		db_conn.close()	

# -> Encapsulated message treat accordingly
	# -> [ id | m_type | data | source | destination_ip | time ]	
	elif m_type == "5":
		#print("MESSAGE FIELDS LENGTH: ", len(message_fields))
		data = '/'.join(message_fields[2:-3])
		#print("DATA: ", data)
		source = message_fields[-3]
		destination_ip = message_fields[-2]
		timest = message_fields[-1]
		
		if(destination_ip != localIP):
			try:
				planned_nexthop = db_access.next_hop_by_destination(db_conn, destination_ip)
			except Exception as e:
				raise e
			all_neighbours = db_access.get_next_hops(db_conn)
			# if peer_ip == planned_nexthop :
			# 	print("ALL NEIGHBOURS: ", all_neighbours)
			# 	nlist = [neigh for neigh in all_neighbours if neigh != planned_nexthop ]
			# 	new_nexthop = random.choice(nlist)
			# 	print(new_nexthop)
			# 	poisoned_route = (local_ID, destination_ip, planned_nexthop, 9223372036854775801)
			# 	db_access.insert_route(db_conn, poisoned_route, 1)
			process_time = time.time_ns()-recv_timestamp
			realtime = int(timest)-process_time
			data = data[:-1]+str(realtime)
			send_encapsulated_message(socket, data, destination_ip)
		else:
			data_fields = data.split("|")
			if(len(data_fields)>1 and data_fields[1] == "3"):
				if rcv_test_message(socket, data_fields, recv_timestamp, source) != 0:
					print("Error! test message wrong size")
			else:
				output_to_app(socket, data)
				latency += time.time_ns() - int(message_fields[-1])
				packets+=1
				if packets == 100:
					print("[",time.strftime('%d-%m-%Y %X', time.gmtime()),"] Latency (last 100 packets): ", round((latency/100)*0.000001, 2), " ms")
					packets = 0
					latency = 0


				





def udp_socket_listen(socket_UDP):
	#> threading
	global off_flag
	active_threads = []
	try:
		while off_flag == 0:
			r,_,_ = select.select([socket_UDP],[],[], 0)
			if r :
				message_recv,(peer_ip, peer_port) = socket_UDP.recvfrom(BUFF_SIZE)
				recv_timestamp = time.time_ns()
				#print("RECEIVED message at %d " % recv_timestamp)
				#print("Received response : " + message_recv.decode()+ "from : " + str(peer_ip)) 
				t2 = threading.Thread(target = receive_packet, args = (socket_UDP, message_recv.decode(), peer_ip, recv_timestamp,))
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
		db_conn = db_access.create_connection(db_dir)
		table_count = db_access.count_routes(db_conn)
		# if table_count>0:
		# 	try:
		# 		ip_list = set_neighbours_peers(db_conn)
				
		# 	except Exception as e:
		# 		print("waiting for more peers... %s"% e)
		db_conn.close()		
		pass

	db_conn = db_access.create_connection(db_dir)
	ip_list = set_neighbours_peers(db_conn)
	db_conn.close()
	#print("VIZINHOS INICIAL: ",ip_list)
	try:
		ask_neighbours_for_cost(socket_UDP, ip_list)
	except Exception as e:
		raise e
	test_routes(socket_UDP)

	while off_flag == 0:
		# db_conn = db_access.create_connection(db_dir)
		# ip_list = db_access.get_next_hops(db_conn)
		# db_conn.close()
		ask_neighbours_for_cost(socket_UDP, ip_list)
		#print("VIZINHOS DEPOIS DO CUSTO: ",ip_list)

		test_routes(socket_UDP)		
		time.sleep(time_between_tests)


	t1.join()
	boot_off(socket_UDP)
	return

def data_plane():
	#->rcv_from_outside through APP_PORT
	global off_flag
	app_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	app_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
	app_socket.bind((localIP, APP_PORT_R))
	
	while off_flag == 0:
		r,_,_ = select.select([app_socket],[],[], 0)
		if r :
			message_recv,(app_ip, app_port) = app_socket.recvfrom(BUFF_SIZE)			
			recv_timestamp = time.time_ns()
			#print("RECEIVED message at %d " % recv_timestamp)
			#print("Received message\nfrom : " + str(app_ip) + "\nTo: "+ socket.inet_ntoa(message_recv[0:4])) 
			ip = socket.inet_ntoa(message_recv[0:4])
			#print("Sending APP message TO: ",ip)
			send_encapsulated_message(app_socket, message_recv.decode(), ip)


	# ->send to overlay as encapsulated packet + time
	
	# -> receive it 
	# -> count metrics 
	#->send_to_outside()

def boot_off(socket):
	#send_goodbye_packet(socket)
	#os.remove(db_dir)
	print("Booting off...")


if __name__ == '__main__':
	db_conn = db_access.create_connection(db_dir)
	if db_conn is not None:
		db_access.create_table(db_conn, db_access.create_peer_routes_table)
		db_conn.close()

		tester_thread = threading.Thread(target=boot_up, args=(10,))
		tester_thread.start()
		data_thread = threading.Thread(target=data_plane)
		data_thread.start()
		# res = input("Send \"x\" to stop peer\n")
		# if res == "x":
		# 	 off_flag = 1

		data_thread.join()
		tester_thread.join()
	
	else:
		print("Can't access table")
		
