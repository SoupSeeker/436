#!/usr/bin/env python3
import socket
from ipaddress import IPv4Interface
from datetime import datetime, timedelta

# Time operations in python
isotimestring = datetime.now().isoformat()
timestamp = datetime.fromisoformat(isotimestring)
# 60secfromnow = timestamp + timedelta(seconds=60)

# Choose a data structure to store your records
# records will have tuples in them
# {(record number, mac, ip, timestamp, acked(bool))}
records = {}

# List containing all available IP addresses as strings
ip_addresses = [ip.exploded for ip in IPv4Interface("192.168.45.0/28").network.hosts()]


# Parse the client messages
# We could have:
#    LIST
#    DISCOVER A1:30:9B:D3:CE:18
#    REQUEST A1:30:9B:D3:CE:18 192.168.45.1 2022-02-02T11:42:08.761340
#    RELEASE A1:30:9B:D3:CE:18 192.168.45.1 2022-02-02T11:42:08.761340
#    RENEW A1:30:9B:D3:CE:18 192.168.45.1 2022-02-02T11:42:08.761340
def parse_message(message):
    try:
        try:
            #in this case, it is either REQUEST, RELEASE, RENEW
            req, mac, ip, time = message.split()
            parsed = req, mac, ip, time
            return parsed
        except:
            pass

        try:
            #in this case, its DISCOVER
            req, mac = message.split()   
            parsed = req, mac  
            return parsed
        except:
            pass

        try:
            #in this case it is a LIST 
            req = message.split()
            parsed = req
            return parsed
        except:
            pass
    except:
        OSError()
    


# Calculate response based on message
def dhcp_operation(parsed_message):
    request = parsed_message[0] #request is always first

    if request == b"LIST":
        print("LIST MESSAGE")
 
      
    elif request == b"DISCOVER":
        request, mac = parsed_message
        if mac in records:  #when getting discover, we check records  
            print("Found mac in records, so check timestamp for expire")  
            
        else:
            print("Not found, trying to add to records")
            if len(records) == 0:
                onemin = timestamp + timedelta(seconds=60)
                newUser = (0, mac, ip_addresses[0], onemin)
                print(records)

            
            
            

    elif request == b"REQUEST":
        print("REQUEST MESSAGE")
        #respond wit hacknowledge

    elif request == b"RELEASE":
        print("RELEASE MESSAGE")
        #get rid of ip?

    elif request == b"RENEW":
        print("RENEW MESSAGE")
        #send ack and time


# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Avoid TIME_WAIT socket lock [DO NOT REMOVE]
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", 9000))
print("DHCP Server running...")

try:
    while True:
        message, clientAddress = server.recvfrom(4096)

        parsed_message = parse_message(message)

        response = dhcp_operation(parsed_message)

        server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()
