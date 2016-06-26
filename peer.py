import socket
import sys
import threading
from threading import Thread
from thread import *
import glob
import os
from os import walk, path, listdir
from os.path import isfile, join
import pickle

BUFSIZE = 4096

path = str(os.getcwd())	

files = [f for f in listdir(path) if isfile(join(path, f))]	#find the files in path	

#print 'path is ' + path
#print files

#host = socket.gethostbyname(socket.gethostname())
#host = socket.gethostbyname(socket.getfqdn())     

peer_dict = {}
print '\n\n'
def peerclient(host, port, s, plisten):
	peer_dict[plisten] = files
	#print peer_dict
	#addport = str(plisten) + ' '.join(files)
	#print addport
	s.connect((host, port))						#connect to index
	print('\nClient is live and connected to the index server now')

	while True:
		print('\nSelect number to\n(1). Register files\n(2). Search file\n(3). Exit\n') 
		userinput = raw_input('>> ')

		if int(userinput) == 1:
		    	print ('\nFiles from ' + path + ' updating to index server')
		    	message = '1\n' + str(plisten) + '\n' + ' '.join(files) #concat
    			#print message
			dumps = pickle.dumps(message)
    	
			try:
				s.send(dumps)
    			except:
    				print 'Cannot Send\n'
				sys.exit()
    	
			reply_message = s.recv(1024)
    	
			print '\n' + reply_message

		elif int(userinput) == 2:
    			stext = raw_input('\nEnter a .txt file to search\n')
    			message = '2\n' + stext
			dumps = pickle.dumps(message)
		
    			try:
        			s.sendall(dumps)
    			except:
        			print 'Cannot Send\n'
        			sys.exit()
    			
			resp = s.recv(1024)
			print resp
			print type(resp)
			
			if str(resp) == "EOF":
				print 'File not found'
				continue

		
			print 'File found in ' + resp
			s_peerid = resp.split(':')[0]
			s_port = resp.split(':')[1]
			s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s1.connect((s_peerid, int(s_port)))
			s1.send(stext)
			rec_file = open(stext, 'w')
	  		while True:
				data = s1.recv(BUFSIZE)
				if not data: break
				rec_file.write(data)
				print 'receiving file'
			rec_file.close()
			print 'file received in your current directory'
			s1.close()
	
		elif int(userinput) == 3:
    			print 'disconnecting from the server'
			message = '3\n' + 'disconnect'
			dumps = pickle.dumps(message) 
			s.send(dumps)			
			s.close()			
			break

		else:
			print 'select a number from menu'

	s.close()

def serverlisten(slisten):
		
	while True:
		sconn, peeraddr = slisten.accept()
		message = sconn.recv(1024)
		try:
			bytes = open('message').read()
		except:
			sconn.sendall('No fIle')
		sconn.send(bytes)
		#print 'File sent'
  	
		sconn.sendall('EOF')
	slisten.close()

if __name__ == '__main__':


	host = ''
	port = 31222
	plisten = 7299
	q = queue.Queue(0)
	threads = []
	
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             
	except socket.error:
 		print 'Socket Create Failed'
		sys.exit()

	slisten = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	slisten.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	#s.connect((host, port))			

	try:
		slisten.bind((host, plisten))
	except socket.error, msg:
		print 'Bind failed' + msg[1]
		sys.exit()
	
	slisten.listen(10)
	print '\nPeer server socket listening at port ' + str(plisten)
	try:
			
		t1 = threading.Thread(target = serverlisten, args = (slisten,)).start()
	 
		t2 = Thread(target = peerclient, args = (host,port,s,plisten)).start()
		#q.put(slisten.accept())
		
	except:
		slisten.close()


