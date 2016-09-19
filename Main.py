#python version 2.7.9

import RPi.GPIO as GPIO
import MFRC522, signal, datetime
import socket, fcntl, struct, platform
import json, urllib2

# def variables
continue_reading = True
MIFAREReader = MFRC522.MFRC522()
url = "http://54.191.101.45:9998/overcart/trace"

# def functions
def _ifinfo(sock, addr, ifname):
	iface = struct.pack('256s', ifname[:15])
	info = fcntl.ioctl(sock.fileno(), addr, iface)
	
	if addr == 0x8927:
		hwaddr = []
		for char in info[18:24]:
			hwaddr.append(hex(ord(char))[2:])
		return ':'.join(hwaddr)
	else:
		return socket.inet_ntoa(info[20:24])

def ifconfig(ifname):
	ifreq = {'ifname': ifname}
	infos = {}
	osys = platform.system()
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	if osys == 'Linux':
		# offsets defined in /usr/include/linux/sockios.h on linux 2.6

		infos['addr'] = 0x8915 # SIOCGIFADDR
		infos['brdaddr'] = 0x8919 # SIOCGIFBRDADDR
		infos['hwaddr'] = 0x8927 # SIOCSIFHWADDR
		infos['netmask'] = 0x891b # SIOCGIFNETMASK

	elif 'BSD' in osys:
		infos['addr'] = 0x8915
		infos['brdaddr'] = 0x8919
		infos['hwaddr'] = 0x8927
		infos['netmask'] = 0x891b

	try:
		for k,v in infos.items():
			ifreq[k] = _ifinfo(sock, v, ifname)
	except:
		pass

	sock.close()
	return ifreq

# capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
	global continue_reading
	print "Ctrl+C captured, ending read."
	continue_reading = False
	GPIO.cleanup()

# hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# bring the MAC address of raspberry pi
MACaddr = ifconfig('wlan0').get('hwaddr')
if MACaddr == None:
	MACaddr = ifconfig('eth0').get('hwaddr')

# start message
print "Press Ctrl-C to stop."

# this loop keeps checking for chips. If one is near it will get the UID and send it to the server
while continue_reading:
	# scan for cards
	(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

	# if a card is found
	if status == MIFAREReader.MI_OK:
		print "card detected"
	
	# get the UID of the card
	(status,uid) = MIFAREReader.MFRC522_Anticoll()

	# if we have the UID, continue
	if status == MIFAREReader.MI_OK:
		data = {
			'rasp_id': MACaddr,
			'card_id': uid[:4],
			'datetime': str(datetime.datetime.now())
		}
		req = urllib2.Request(url)
		req.add_header('Content-Type','application/json; charset=utf-8')

		jsondata = json.dumps(data)
		jsondataasbytes = jsondata.encode('utf-8')
		req.add_header('Content-Length',len(jsondataasbytes))

		res = urllib2.urlopen(req, jsondataasbytes)
		print(res.read().decode('utf-8'))
