from socket import socket, AF_INET, SOCK_DGRAM
from packet import *
from threading import Thread
import signal
import sys

#Creates new router
class udprouter():

        # For sake of assignment I am letting each router know eachothers rt
        def __init__(self, id, port):
                self.port = port
                self.id = id
                self.rt = { 'routes': [{'id': 101, 'ip': '192.168.1.1', 'gateway': '192.168.1.2', 'port':8880},
                {'id': 202, 'ip': '10.0.1.1', 'gateway': '10.0.1.0', 'port':8882}] }

        # Using the dst received in packet finds the corresponding dst address
        def search_dst_addr(self, dst):
                for x in range(len(self.rt['routes'])):
                        if self.rt['routes'][x]['id'] == dst:
                                return (self.rt['routes'][x]['ip'], self.rt['routes'][x]['port'])
                return ('10.0.1.1', 8882)

        # Sends packet to dst address
        def handle_sending(self, packet, server):
                s = socket(AF_INET, SOCK_DGRAM)
                s.sendto( packet, server )
                print('Sending To: ', server)
                s.close()
                return 0

        # Waits to receive a packet and if the correct type starts new thread to sent that packet
        def handle_packets(self):
                s = socket(AF_INET, SOCK_DGRAM)
                signal.signal(signal.SIGINT, sig_handler)
                s.bind(('0.0.0.0', self.port))
                while True:
                        packet, addr = s.recvfrom(1024)
                        print("Received From: ", addr)
                        type, ttl, src, dest, dest2, dest3, kval, data = read_packet(packet)
                        """ ADD k/n here"""
                        if dest2 is None and dest3 is None:
                            # pass packet to next router
                            server = self.search_dst_addr(dest)
                            thread = Thread(target=self.handle_sending(packet,server))
                            thread.start()
                        elif dest2 is not None and dest3 is None:
                            # 2 potential destinations, do k/n
                            if kval==1:
                                if self.search_dst_addr(dest) == self.search_dst_addr(dest2):
                                    #same route
                                    server = self.search_dst_addr(dest)
                                    packet = create_packet(type, ttl=ttl, src=src, dest=dest, kval=1, data=data)
                                    thread = Thread(target=self.handle_sending(packet,server))
                                    thread.start()
                                else:
                                    # different routes, so must choose the shortest path. request link state packet from both destinations and compare
                                    if:
                                        pass
                                    else:
                                        pass
                            else:
                                #kval is 2
                                if self.search_dst_addr(dest) == self.search_dst_addr(dest2):
                                    # same route
                                    server = self.search_dst_addr(dest)
                                    thread = Thread(target=self.handle_sending(packet,server))
                                    thread.start()
                                else:
                                    # different routes, so must send over both paths bc k == n
                                    for dst in (dest, dest2):
                                        server = self.search_dst_addr(dst)
                                        packet = create_packet(type, ttl=ttl, src=src, dest=dst, kval=1, data=data)
                                        thread = Thread(target=self.handle_sending(packet,server))
                                        thread.start()
                        else:
                            if kval==1:
                                pass
                            elif kval==2:
                                pass
                            else:
                                pass
                            # 3 potential distinations, do k/n
                            pass


                s.close()
                return 0

def sig_handler(sig, frame):
    print("User requested router to be removed. Removing now...")
    s.close()
    sys.exit("Connection terminated successfully")

if __name__ == '__main__':
        print("Router Started...")
        udp_router = udprouter(id=201, port=8881)
        udp_router.handle_packets()
