from icmplib import ping, multiping, traceroute, resolve
from icmplib import async_ping, async_multiping, async_resolve
from icmplib import ICMPv4Socket, ICMPv6Socket, AsyncSocket, ICMPRequest, ICMPReply
import sys

dest_address='10.0.5.2'




if __name__ == '__main__':
	
	Hop = traceroute(sys.argv[1])
	print(Hop)