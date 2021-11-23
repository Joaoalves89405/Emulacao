import time, sys
from time import sleep 
import ntplib
from datetime import datetime

def get_ntp_time( source ):
	ntp_pool = '0.pool.ntp.org'

	call = ntplib.NTPClient()
	response = call.request(source, version=3)
	try:
		t=response.orig_time
		return t
	except Exception as e:
		print(e)
		raise


if __name__ == "__main__":

	now = get_ntp_time('0.pool.ntp.org')
	runat = time.time()+1
	print ("NTP time: %s" % now)
	print ("My time: %s" % runat)
	print ("Time to wait: %s" % (runat - now))
	sleep((runat-now))

	localbefore = time.time()
	print("Running...")
	now = get_ntp_time()
	localafter = time.time()
	print ("NTP time: %s" % now)
	print ("Job ran at:  %s" % (now - (localafter - localbefore)))
