import time
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import select
import random
import asyncore
import numpy as np


def create_packet(type, ttl=None, src=None, dest=None, dest2=None, dest3=None, kval=None, data=None):
    if type=="hello":
        # Type(2), ttl(4), src(4)
        type = 0
        header = struct.pack("HLL", type, ttl, src)
        return header

    elif type=="data":
        # Type(2), src(4), kval(2), dest(4), dest2(4), dest3(4), data(1000)
        type = 1
        header = struct.pack("HLHLLL", type, src, kval, dest, dest2, dest3)
        return header + bytes(data, 'utf-8')

    elif type=="ack":
        # Type(2), src(4), dest(4)
        type = 2
        header = struct.pack("HLL", type, src, dest)
        return header

    elif type=="ls":
        type = 3
        header = struct.pack("HLL", type, src, dest)
        return header + bytes(data, 'utf-8')

    else:
        return None


def read_packet(pkt, ttl=None, src=None, dest=None, dest2=None, dest3=None, kval=None, data=None):
    type = struct.unpack("H",pkt[0:2])
    if type==0:
        ttl, src = struct.unpack("LL", pkt[2:10])
        return type, ttl, src
    elif type==1:
        src, kval, dest, dest2, dest3 = struct.unpack("LHLLL", pkt[2:20])

        return type, src, kval, dest, dest2, dest3, pkt[20:]

    elif type==2 or type==3:
        src, dest = struct.unpack("LL", pkt[2:10])
        return type, src, dest, data
        
    else:
        return type, ttl, src, dest, dest2, dest3, kval, data


###################################
####   Assignment Code Below   ####
###################################

#Starts a ping from current host (src) to desired destination (dst)
def ping(h, c, dst):
    seq_num, nor, rtt = 0, 0, []
    #count = 0
    for x in range(c):
        #count += 1
        # Creates and sends the request packet
        packet = create_packet(1, h.id, dst, seq=seq_num, data='This is assignment 5!')
        send_packet(h, packet)
        send_time = time.time()

        # Waits to receive a reply packet to move onto next ping
        seq_failed = receive_packet(h, packet)
        if seq_failed == -1:
            rtt.append(time.time()-send_time)
            seq_num += 1
        else:
            x -= 1
            nor += 1
            print("Retransmitting packet with seq num: ", seq_num)
    rtt = np.array(rtt)
    #print(count)
    print(c, " packets transmitted, ", nor, " packets retransmitted, ", (nor/c)*100, "% packet loss",
         "\n round-trip min/avg/max/stddev = ", np.min(rtt),"/",np.mean(rtt),"/",np.max(rtt),"/",np.std(rtt), " s" )
    return 0

# Sends a packet across UDP socket the corresponding router gateway for that host
def send_packet(h, packet):
    s = socket(AF_INET, SOCK_DGRAM)
    s.sendto(packet, h.default_gateway)
    s.close()
    print("Sending: ", packet, " To: ", h.default_gateway)
    return 0

# Receives packets across UDP socket
def receive_packet(h, sent_packet):
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind((h.ip, h.port))
    seq_failed = -1

    #Waits to receive packet on h.ip/h.port
    while True:
        try:
            if sent_packet != None:
                s.settimeout(0.007)
            packet,addr = s.recvfrom(1024)
            pkttype, pktlen, dst, src, seq = read_header(packet)
        except OSError:
            pkttype, pktlen, dst, src, seq = read_header(sent_packet)
            seq_failed = seq
            break

        if(pkttype == 1 and dst == h.id):
            print("Received: ", packet, " From: ", src)

            # Creates reply packet
            packet = create_packet(2, h.id, src, 0, 'This is a reply!')
            send_packet(h, packet)

        # Checks for reply packet (Note this is not very flexable and would break the server if it receives reply packet)
        elif(pkttype == 2 and dst == h.id):
            #data = read_data(packet)
            print("Receved: ", packet, " From: ", src)
            break

    s.close()
    return  seq_failed