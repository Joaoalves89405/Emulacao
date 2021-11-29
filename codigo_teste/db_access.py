import sqlite3


create_routes_table = """CREATE TABLE "routes_table" (
							"route_id"	INTEGER NOT NULL UNIQUE,
							"source"	TEXT NOT NULL,
							"destination"	TEXT UNIQUE,
							"next_hop"	TEXT,
							"cost"	REAL,
							PRIMARY KEY("route_id" AUTOINCREMENT)
						);"""
	

def create_table(conn, create_table_sql):
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
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

	sql = ''' INSERT INTO routes_table(source, destination, next_hop, cost)
				VALUES(?,?,?,?)
				ON CONFLICT(destination) DO UPDATE SET next_hop = CASE
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

def select_route_by_destination(conn, destination):

	cur = conn.cursor()
	cur.execute('SELECT * FROM routes_table WHERE destination=?', (destination,))

	line = cur.fetchall() 
	
	print(line)
	return 0 


def check_cost(conn, destination):

	cur = conn.cursor()
	try:
		cur.execute('SELECT cost FROM routes_table WHERE destination=?', (destination,))
		cost = cur.fetchall()
	except Exception as e:
		print("There's no destination with that IP")
	print(cost)


if __name__ == '__main__':

	


	route1 = ("10.0.0.2","10.0.0.3", "10.0.20.5", 54)
	conn = create_connection("test2_db.db")

	if conn is not None:

		create_table(conn, create_routes_table)
		insert_route(conn, route1)
		select_route_by_destination(conn, "10.0.0.3")
		check_cost(conn, "10.0.0.3")

	else :
		print ("Error! Cannot create the database connection.")
