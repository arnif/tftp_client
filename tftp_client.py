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
	print "python tftp_client.py localhost get texti.txt"
	print "python tftp_client.py localhost put texti.txt"
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
		s.sendto(sendpacket,(host,port))

		try:
			createFile = open(filename, 'w')
		except Exception:
			print "Can't open " , filename

		totalDatalen = 0
		blockCount = 1
		errors = 0

		while True:
			while errors < 3:
				try:
					data, remoteSocket = s.recvfrom(4096)
					Opcode = struct.unpack('!H', data[0:2])[0]
					errors = 0
					break
				except Exception:
					s.sendto(sendpacket, (host,port))
					Opcode = 'Timeout'
					errors += 1

			if Opcode == 3:
				blockNo = struct.unpack('!H',data[2:4])[0]
				if blockNo != blockCount:
					print('wrong block')
					createFile.close()
					break

				blockCount +=1
				if blockCount == 65536:
					blockCount = 1

				dataPayload = data[4:]

				try:
					createFile.write(dataPayload)
				except Exception:
					print('cant write data')
					createFile.close()
					break

				totalDatalen += len(dataPayload)
				sendpacket = struct.pack(b'!2H', 4, blockNo)
				s.sendto(sendpacket, remoteSocket)

				if len(dataPayload) < 512:
					print('have enough, bye')
					createFile.close()
					break

			elif Opcode == 5:

				errCode = struct.unpack('!H',data[2:4])[0]
				errString = data[4:-1]
				print('Error code: ', errCode)
				createFile.close()
				break

			elif Opcode == 'Timeout':
				print('Timed out')
				createFile.close()

			else:
				print('Unknown error')
				createFile.close()

		


	elif action == 'put':
		sendpacket = conStruct(2,filename,mode)


	

	

	


def conStruct(opcode,filename,mode):
 return  struct.pack('!H' + str(len(filename)+1) + 's6s', opcode , filename,mode)
    
    


if __name__ == "__main__":
	main()