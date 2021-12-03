import sqlite3
import socket


create_peer_routes_table = """CREATE TABLE "routes_table" (
							"route_id"	INTEGER NOT NULL UNIQUE,
							"source"	INTEGER NOT NULL,
							"destination"	TEXT UNIQUE,
							"next_hop"	TEXT,
							"cost"	REAL,
							"last_checked" INTEGER,
							PRIMARY KEY("route_id")
						);"""
	
create_server_tables = """CREATE TABLE "routes_table" (
							"route_id"	INTEGER NOT NULL UNIQUE,
							"source"	TEXT NOT NULL,
							"destination"	TEXT UNIQUE,
							"next_hop"	TEXT,
							"cost"	REAL,
							"last_checked" INTEGER,
							FOREIGN KEY("source") REFERENCES "peer_table"("peer_id")
							ON DELETE CASCADE,
							PRIMARY KEY("route_id" AUTOINCREMENT)
							);
						CREATE TABLE "peer_table" (
							"peer_id"	INTEGER NOT NULL UNIQUE,
							"state"	INTEGER,
							"area"	INTEGER,
							"ip_address"	TEXT UNIQUE,
							PRIMARY KEY("peer_id" AUTOINCREMENT)
							);"""

def create_table(conn, create_table_sql):

		try:
			c = conn.cursor()
			c.executescript(create_table_sql)
		except Exception as e:
			print(e)

def create_connection(db_file):
	conn = None

	try:
		conn = sqlite3.connect(db_file)
		print("Connected %s" % sqlite3.version)
		return conn
	except Exception as e:
		print(e)
		raise
	finally:
		# if conn:
		# 	conn.close()
		pass

		return conn
			

#Only insert route if cost is lower 
##### route(sourceIP, destinationIP, next_hop, cost)####
def insert_route(conn, route):

	sql = ''' INSERT INTO routes_table(source, destination, next_hop, cost, last_checked)
				VALUES(?,?,?,?, strftime('%s','now'))
				ON CONFLICT(destination) DO UPDATE SET 
					last_checked = excluded.last_checked,
					next_hop = CASE
					WHEN cost > excluded.cost THEN excluded.next_hop
					ELSE next_hop
					END,
					cost = CASE
					WHEN cost > excluded.cost THEN excluded.cost
					ELSE cost
					END
				WHERE destination IN (excluded.destination);'''

	cur = conn.cursor()
	cur.execute(sql, route)
	conn.commit()

	return cur.lastrowid

def delete_route(conn, route_id):

	sql = 'DELETE FROM routes_table WHERE route_id'
	cur = conn.cursor()
	cur.execute(sql,(id,))
	conn.commit()

def delete_route_by_destination(conn, destination):

	cur = conn.cursor()
	try:
		cur.execute('DELETE * FROM routes_table WHERE destination=?', (destination,))
		line = cur.fetchone() 
		print(line)
		return 0
	except Exception as e:
		print(e)
		return 1

def select_route_by_destination(conn, destination):

	cur = conn.cursor()
	try:
		cur.execute('SELECT * FROM routes_table WHERE destination=?', (destination,))
		line = cur.fetchone() 
		print(line)
		return line
	except Exception as e:
		print("")


def check_cost_from_destination(conn, destination):

	cur = conn.cursor()
	try:
		cur.execute('SELECT cost FROM routes_table WHERE destination=?', (destination,))
		cost = cur.fetchone()[0]
	except Exception as e:
		print("There's no destination with that IP")
	print(cost)
	return cost


#Server function to get all routes from a peer
def insert_peer(conn, peer):
	cur = conn.cursor()
	sql = '''INSERT OR IGNORE INTO peer_table( state, area, ip_address)
				VALUES(?,?,?)ON CONFLICT(ip_address) DO UPDATE SET 
					state = excluded.state;'''
	try:
		cur.execute(sql, peer)
		conn.commit()
		return 0
	except Exception as e:
		print(e)
		return 1

def delete_peer(conn, peer_id):
	cur = conn.cursor()
	sql = 'DELETE FROM peer_table WHERE peer_id = ?'
	
	try:
		cur = conn.cursor()
		cur.execute(sql,(int(peer_id),))
		conn.commit()
		return 0

	except Exception as e:
		print(e)
		return 1

def get_peer_routes(conn, peer_id):
	cur = conn.cursor()
	try:
		cur.execute('''SELECT * FROM routes_table WHERE source=?''',(int(peer_id),))
		routes_list = cur.fetchall()
		pass
	except Exception as e:
		print(e)
		return 1

	print(routes_list)

def get_peerID(conn, ip_address):
	cur = conn.cursor()
	sql = '''SELECT peer_id FROM peer_table WHERE ip_address=?'''
	try:
		cur.execute(sql, (ip_address,))
		peer_id = cur.fetchone()[0]
		return peer_id
	except Exception as e:
		print(e)
		return 1

def get_peer_state(conn, peer_id):
	cur = conn.cursor()
	try:
		cur.execute('''SELECT state FROM peer_table WHERE peer_id=?''',(int(peer_id),))
		status = cur.fetchone()[0]
		return status
	except Exception as e:
		print(e)
		return 1

def set_peer_state(conn, peer_id, status):
	cur = conn.cursor()
	sql= '''UPDATE peer_table SET state = ? WHERE peer_id=?'''

	try:
		cur.execute(sql,(int(status),int(peer_id),))
		conn.commit()
		return status
	except Exception as e:
		print(e)
		return 1

def get_allpeer_ip(conn):
	cur = conn.cursor()
	try:
		sql = '''SELECT ip_address FROM peer_table'''
		cur.execute(sql)
		ip_list = cur.fetchall()
		return ip_list
	except Exception as e:
		print(e)
		return 1


if __name__ == '__main__':

	PeerID = 10500

# 	route0 = (PeerID+1,PeerID,"127.0.0.1","127.0.0.1",0)
# 	route1 = (PeerID,"10.0.20.5", "10.0.0.5", 54)
# 	route2 = (PeerID,"10.0.30.5", "10.0.0.4", 32)
# 	route3 = (PeerID,"10.0.40.5", "10.0.0.6", 104)
# 	route4 = (PeerID,"10.0.50.5", "10.0.0.7", 17)

# 	routes = {route1,route2,route3,route4}

# 	conn = create_connection("DB_peer.db")

# 	if conn is not None:

# 		create_table(conn, create_peer_routes_table)
# 		cur = conn.cursor()

# ##always the first insert operation on peer##
# 		cur.execute(''' INSERT INTO routes_table(route_id, source, destination, next_hop, cost, last_checked)
# 				VALUES(?,?,?,?,?, strftime('%s','now'))''', route0)
		
# 		for route in routes:
# 			insert_route(conn, route)	
# 		val = input("Please enter a destination to check the route: ")
# 		select_route_by_destination(conn, val)
# 		check_cost_from_destination(conn, val)

# 	else :
# 		print ("Error! Cannot create the database connection.")

####################################################
	
	
	peer1 = (PeerID,1,5,"10.0.0.2")
	peer2 = (PeerID+50,1,5,"10.0.0.3")
	peer3 = (PeerID+100,0,3,"10.0.10.1")
	peer4 = (PeerID+150,1,2,"10.0.20.2")
	
	peers = {peer1, peer2, peer3, peer4}
	

	route1 = (PeerID,"10.0.20.5", "10.0.0.5", 54)
	route2 = (PeerID,"10.0.30.5", "10.0.0.4", 32)
	route3 = (PeerID,"10.0.40.5", "10.0.0.6", 104)
	route4 = (PeerID,"10.0.50.5", "10.0.0.7", 17)

	routes = {route1,route2,route3,route4}
	hostname=socket.gethostbyname(socket.gethostname())

	conn = create_connection("/%s_str/DB_server.db" % hostname)

	if conn is not None:

		create_table(conn, create_server_tables)
		cur = conn.cursor()

		for peer in peers:
			insert_peer(conn, peer)

		for route in routes:
			insert_route(conn, route)

		#delete_peer(conn, PeerID)
		set_peer_state(conn, PeerID, 1)
		

	else :
		print ("Error! Cannot create the database connection.")

