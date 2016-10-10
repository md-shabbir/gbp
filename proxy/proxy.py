import os
import select
import socket
import sys
import Queue
import time

try:
    #os.unlink("/tmp/uds_socket_test")
    os.unlink("/var/run/uds_socket")
except Exception:
    pass

# Create a TCP/IP socket
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.setblocking(0)
#print 'SERVER: ', server.fileno()
# Bind the socket to the port
server_address = "/var/run/uds_socket"
print >>sys.stderr, 'starting up on %s ' % server_address
server.bind(server_address)

# Listen for incoming connections
server.listen(5)

# List of sockets which we expect to read/write
active_sockets = [ server ]
clients_socket = []
# Outgoing message queues (socket:Queue)
message_queues = {}

#message_queues[server] = Queue.Queue()

# Proxy connections map {socket1:socket2}
proxy_map = {}

tcp = []

count = 0

#log = open('log.txt', 'w')
#import pdb;pdb.set_trace()


def proxy(unix_socket):
    #tcp_server_address = ('11.0.0.55', 8070)
    tcp_server_address = ('localhost', 8080)
    try:
    	tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#tcp_socket.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    	tcp_socket.connect(tcp_server_address)
    except Exception, e:
	    print 'Error in connection to pecan server', e
	    return unix_socket, None

    proxy_map[unix_socket] = tcp_socket
    proxy_map[tcp_socket]  = unix_socket
    
    print "@@@ PROXY - unix - %d, tcp - %d" %(unix_socket.fileno(), tcp_socket.fileno())
    return unix_socket, tcp_socket


def serve_next():
    if not clients_socket:
        return
    s = clients_socket[0]
    uc, tc = proxy(s)
    if tc == None:
	    s.close()
	    clients_socket.remove(s)
	    serve_next()
    else:
    	uc.setblocking(0)
    	tc.setblocking(0)
    
    	message_queues[uc] = Queue.Queue()
    	message_queues[tc] = Queue.Queue()
    	active_sockets.append(uc)
    	active_sockets.append(tc)
    	global count
    	count += 1
    	tcp.append(tc)

def remove(s):
    print 'in remove'
    if s in tcp:
	    tcp.remove(s)
    try:
	    if s in clients_socket:
		    clients_socket.remove(s)
    	    active_sockets.remove(s)
    	    del message_queues[s]
	    del proxy_map[s]
    except Exception, e:
	    print 'Remove: ', e


def close(s):
    print 'in close'
    #if not message_queues[s].empty():
#	print 'QUEUE is not empty'
 #   if s in tcp:
#	tcp.remove(s)
    
    try:
        s.shutdown(socket.SHUT_RDWR)
        s.close()
	proxy_map[s].close()
    except Exception as exc:
        print 'error in closing socket, ',exc
    
    remove(proxy_map[s])
    remove(s)
    serve_next()


while True:
	try:
	    time.sleep(0.1)
	    # Wait for at least one of the sockets to be ready for processing
	    # print >>sys.stderr, '\nwaiting for the event on sockets'
	    w_sockets = list(active_sockets)
	    w_sockets.remove(server)
	    readable, writable, exceptional = select.select(active_sockets, w_sockets, [], 1)

	    # Handle outputs
	    for s in writable:
	    # for s in sockets:
		print 'in write'
		print >>sys.stderr, "socket - %d is writable" %(s.fileno())
		if s is server:
		    continue

		try:
		    next_msg = message_queues[proxy_map[s]].get_nowait()
		    print >>sys.stderr, 'Queue for socket - %d, data len %d' %(proxy_map[s].fileno(), len(next_msg))
		except Queue.Empty:
		    # No messages waiting so stop checking for writability.
		    # print >>sys.stderr, 'output queue for', s.getpeername(), 'is empty'
		    print >>sys.stderr, "socket - %d is writable" %(s.fileno())
		    print >>sys.stderr, 'Queue for socket - %d is empty' %(proxy_map[s].fileno())
		    pass
		except Exception as exc:
		    import pdb;pdb.set_trace()
		else:
		    try:
		        s.sendall(next_msg)
		    except Exception as exc:
		        print "@@@ Socket - %d, got exception in sending - %s" %(s.fileno(), exc)
		        message_queues[proxy_map[s]].put(next_msg)

	    # Handle inputs
	    for s in readable:
		print 'in read'
		#print 'SIZE1: ', len(readable)
		if s is server:
		    print 'server accept in'
		    # A "readable" server socket is ready to accept a connection
		    connection, client_address = s.accept()
		    clients_socket.append(connection)
		    #print 'SIZE2: ', len(clients_socket)
		
		    # check for first client connection and serve
		    if len(clients_socket) == 1:
			    serve_next()
		
		else:
		    data = s.recv(1024*1024)
		    if data:
		        print >>sys.stderr, 'Queue for socket - %d, updating len - %d' % (s.fileno(), len(data))
		        message_queues[s].put(data)
			#print 'RECEIVED: ', data
		    else:
		        # Interpret empty result as closed connection
		        print >>sys.stderr, 'closing', client_address, 'after reading no data'
		        
		        #close(proxy_map[s])
			#print 'CLOSED FIRST: '
			#if s in tcp:
			#	print 'TCP'
			#else:
			#	print 'UNIX'

		        # Stop monitoring this socket and its corresponding socket	
		        close(s)


	    # Handle "exceptional conditions"
	    for s in exceptional:
		print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
		# Stop monitoring connection
		close(proxy_map[s])
		close(s)
	except KeyboardInterrupt, e:
		print 'Count: ', count
		print 'Active sockets: ', len(active_sockets)
		sys.exit(1)
	except Exception, e:
		#if s in tcp:
		#	tcp.remove(s)
		print 'Main: ', e
		#print s.fileno()
		#if clients_socket:
		#	print 'clients not empty'
		#if active_sockets:
		#	print 'active socket not empty'


class Proxy(object):

    def __init__(self):
        # mapping of unix socket and tcp sockets
        self.proxy_map = {}
        # all active sockets (unix + tcp sockets)
        self.active_socket = []
        # client socket (only unix socket)
        self.client_socket = []
        self.message_queues = []

    def socket_map(self, unix_socket, tcp_socket)
        self.proxy_map[unix_socket] = tcp_socket
        self.proxy_map[tcp_socket] = unix_soxket

    def server_socket(self, server_address="/var/run/uds_socket"):
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.setblocking(0)
        #print 'SERVER: ', server.fileno()
        # Bind the socket to the port
        print >>sys.stderr, 'starting up on %s ' % server_address
        server.bind(server_address)
        # Listen for incoming connections
        server.listen(5)

    def tcp_connection(self):
        #tcp_server_address = ('11.0.0.55', 8070)
        tcp_server_address = ('localhost', 8080)
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #tcp_socket.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            tcp_socket.connect(tcp_server_address)
        except Exception, e:
            print 'Error in connection to pecan server', e
            return None

        print "@@@ tcp - %d" % (tcp_socket.fileno())
        return tcp_socket

    def serve_next(self):
        if not clients_socket:
            return
        uc = clients_socket[0]
        tc = tcp_connection()
        if tc == None:
            us.close()
            clients_socket.remove(us)
            serve_next()
        else:
            uc.setblocking(0)
            tc.setblocking(0)

            message_queues[uc] = Queue.Queue()
            message_queues[tc] = Queue.Queue()
            active_sockets.append(uc)
            active_sockets.append(tc)
            #global count
            #count += 1
            tcp.append(tc)
 
