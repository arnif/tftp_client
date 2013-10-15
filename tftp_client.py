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

	#ef ekki er slegid inn rettur fjoldi argv er notandanum kennt ad nota forritid
	if len(sys.argv) < 4: 
		usage()

	host = sys.argv[1]
	action = sys.argv[2]

	#passa ad taka a moti ha og la stofum
	if 'put' not in action.lower():
		if 'get' not in action.lower():
			usage()

	filename = sys.argv[3]
	mode = 'octet'

	#opna socket
	try:
		s = socket(AF_INET, SOCK_DGRAM)
		s.settimeout(10)

		print 'Connected to ', host
	except Exception:
		print 'Could not connect', Exception


	#get adgerdin, RRQ request
	if action == 'get':
		#Kallad a construct sem byr til pakka sem sendir RRQ request 
		sendpacket = conStruct(1,filename,mode)
		#Pakkinn sendur a server
		s.sendto(sendpacket,(host,port))

		#reyni ad bua til skjal
		try:
			createFile = open(filename, 'wb')
		except Exception:
			print "Can't open " , filename

		totalDatalen = 0

		while True:
			#fa gogn fra servernum
			try:
				data, remoteSocket = s.recvfrom(4096)
				Opcode = struct.unpack('!H', data[0:2])[0]
			except Exception:
				Opcode = 'Timeout'

			#saekjir gognin ur skjalinu
			#Ef server sendir til baka DATA
			if Opcode == 3:
				blockNo = struct.unpack('!H',data[2:4])[0]
				dataStuff = data[4:]

				try:
					createFile.write(dataStuff)
				except Exception:
					print("Can't write data")
					createFile.close()
					break

				totalDatalen += len(dataStuff)
				sendpacket = struct.pack(b'!2H', 4, blockNo)
				s.sendto(sendpacket, remoteSocket)

				#ef staerdin a gognunum i skjalinu er ordid minna en 512 bytes
				#tha lokar thad skjalinu
				if len(dataStuff) < 512:
					print('File transfer completed. Thank you come again.')
					createFile.close()
					break

			#ef upp kemur villa
			#Server sendir villu til baka
			elif Opcode == 5:

				errCode = struct.unpack('!H',data[2:4])[0] 
				errString = data[4:-1] 
				print('Error code: ', errCode, 'Error: ', errString)
				createFile.close()
				break

			elif Opcode == 'Timeout':
				print('Timed out')
				createFile.close()

			else:
				print('Unknown error')
				createFile.close()



	#put adgerdin, WRQ request	
	elif action == 'put':
		#Kallad a construct sem byr til pakka sem sendir WRQ request
		sendpacket = conStruct(2,filename,mode)
		#pakkinn sendur a server
		s.sendto(sendpacket,(host,port))

		#les skjalid
		try:
			sendFile = open(filename, 'rb')
		except Exception:
			print "Can't open " , filename

		totalDatalen = 0

		while True:
			#fa gogn fra servernum
			try:
				data, remoteSocket = s.recvfrom(4096)
				Opcode = struct.unpack('!H', data[0:2])[0]

			except Exception:
				opcode = 'Timeout'

			#skrifar gogn af client skjalinu a server skjalid
			#Ef serverinn sendir fra ser ACK	
			if Opcode == 4:
				blockNo = struct.unpack('!H', data[2:4])[0]
				blockNo +=1
				dataChunk = sendFile.read(512)
				dataPacket = struct.pack(b'!2H', 3, blockNo) + dataChunk
				s.sendto(dataPacket, remoteSocket)
				totalDatalen += len(dataChunk)

				#ef staerdin a gognunum i skjalinu er ordid minna en 512 bytes
				#tha lokar thad skjalinu
				if len(dataChunk) < 512:
					print('File has been sent. Thank you come again.')
					sendFile.close()
					break

			#ef upp kemur villa
			#Server sendir Error til baka
			elif Opcode == 5:

				errCode = struct.unpack('!H', data[2:4])[0]
				errString = data[4:-1]
				print('Error code ', errCode, ' Error: ' ,errString)
				sendFile.close()
				break

			elif Opcode == 'Timeout':
				print('Timed out')
				sendFile.close()

			else:
				print('Unknown error')
				sendFile.close()



#2 bytes     string    1 byte     string   1 byte
#------------------------------------------------
#| Opcode |  Filename  |   0  |    Mode    |   0  |
#------------------------------------------------
#utfaerir upphafspakkann. Kallad a tetta fall tegar er notad put og get og ta er opcode
#annadhvort 1 eda 2. 
def conStruct(opcode,filename,mode):
 return  struct.pack('!H' + str(len(filename)+1) + 's6s', opcode , filename,mode)
    
    
if __name__ == "__main__":
	main()