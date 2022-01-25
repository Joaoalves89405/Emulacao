all: peer clean

peer: codigo_teste/peer_node.py streaming/client.py
	python3 -u ./codigo_teste/peer_node.py>log_peer.txt & python3 ./streaming/client.py

clean:
	pkill -9 python3