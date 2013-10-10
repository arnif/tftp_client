from socket import*
import struct
import sys

port = 69

def usage():
	#fall sem utskyrir hvernig nota skal clientinn
	print ""
	print "Usage: tftp_client [SERVER] [ACTION] [FILE]"
	print ""
	print "SERVER:"
	print "ex: 127.0.0.1 or nameofserver.is"
	print ""
	print "ACTION:"
	print "put : to upload file"
	print "get : to download file"
	print ""
	print "FILE:"
	print "name of the file you want to put/get"
	print ""
	print "Examples:"
	print "tftpC tserver.ru.is get texti.doc"
	print "tftpC tserver.ru.is put texti.doc"
	print ""

	sys.exit(1)


def main():

	if len(sys.argv) < 4:
		usage()

	host = sys.argv[1]
	action = sys.argv[2]

	if 'put' not in action.lower():
		if 'get' not in action.lower():
			usage()

	filename = sys.argv[3]
	mode = 'octet'

	s = socket(AF_INET, SOCK_DGRAM)
	s.settimeout(10)

	print 'connection'


	if action == 'get':
		sendpacket = conStruct(1,filename,mode)
	elif action == 'put':
		sendpacket = conStruct(2,filename,mode)

	#print sendpacket

	s.sendto(sendpacket,(host,port))

	# data = s.recvfrom(512)
	# print data

	createFile = open(filename, 'w')

	data, remoteSocket = s.recvfrom(4096)
	Opcode = struct.unpack('!H', data[0:2])[0]

	createFile.write(data)
	createFile.close()

	


def conStruct(opcode,filename,mode):
 return  struct.pack('!H' + str(len(filename)+1) + 's6s', opcode , filename,mode)
    
    


if __name__ == "__main__":
	main()