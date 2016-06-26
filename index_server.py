# socketserverthread.py
import socket
import sys
import os 
from os.path import isfile, join
from os import walk, path, listdir
import glob
import pickle
from thread import *
from threading import Thread, Semaphore
from time import sleep


if __name__ == "__main__":
    HOST = '' #should be changed to default!
    PORT = 31222

    print 'Welcome to the central index server'
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print 'Socket Created'

try:
    s.bind((HOST, PORT))

except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

#print 'Socket bind complete'

s.listen(10)
print '\n\nSocket now listening for peers'

#activePeers = []
#users = {}
index_dict = {}
dict_lock = Semaphore(1)


def client(conn, peerid):
    sub_dict = {}
    while True:
	#receiving data from peer aa pickle dumps and load it   
        peerdumps = conn.recv(1024)        
	peerdata = pickle.loads(peerdumps)
        #print peerdata
	print '\nReceived data from ' + peerid[0]

	#check the peer information
        if int(peerdata.split('\n')[0]) == 1:
	    sub_dict[peerdata.split('\n')[1]] = peerdata.split('\n')[2]
	    dict_lock.acquire()
 	    #if not index_dict:
	    index_dict.update(sub_dict)
	    #index_dict[peerid] = sub_dict
	    #else:
	    #index_dict[peerid].append(sub_dict)
	    
	    print index_dict
            
            print 'Index updated with files from ' + peerid[0]
            conn.send('All files updated')
	    dict_lock.release()
        elif int(peerdata.split('\n')[0]) == 2:
	    print '\nsearching file ' + peerdata.split('\n')[1] + ' in index server'

	    search = peerdata.split('\n')[1]		
	    for getpeerid in index_dict.keys():
		for getplisten in index_dict[getpeerid].keys():
			if search in index_dict[getpeerid][getplisten]:
				s_port  = getplisten
				s_id = getpeerid[0]
				s_peerid = s_id + ':' + s_port
			else:
				s_peerid = 'EOF'
		

	    #print s_port
	    #print s_id
	    print s_peerid
            	
 	    conn.send(s_peerid)			
      	    
        elif int(peerdata.split('\n')[0]) == 3:
	    print 'Disconnecting with ' + peerid[0]
      	    break
	
	else:
	    continue

    conn.close() 

while True:
    conn, peerid = s.accept()
    
    print '\nA new peer connected ' + peerid[0] + ':' + str(peerid[1])
    start_new_thread(client, (conn,peerid))

s.close()








