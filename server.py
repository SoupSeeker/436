#!/usr/bin/env python3
import socket
from ipaddress import IPv4Interface
from datetime import datetime, timedelta

# Time operations in python
# isotimestring = datetime.now().isoformat()
# timestamp = datetime.fromisoformat(isotimestring)
# 60secfromnow = timestamp + timedelta(seconds=60)

# Choose a data structure to store your records
# records will have tuples in them
# {(record number, mac, ip, timestamp, acked(bool))}
records = list()

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
    request = request.decode("utf8")
    if request == "LIST":
        print("LIST MESSAGE")
 
      
    elif request == "DISCOVER":
        request, mac = parsed_message
        mac = mac.decode("utf8")
        for rec in records:
            if mac in rec:
                isotimestring = datetime.now().isoformat()    
                timestamp = datetime.fromisoformat(isotimestring)   
                old = rec[3]

                if old > timestamp:
                    print("Still valid, just acknowledge")
                    rec[4] = True
                    response = "ACKNOWLEDGE " + mac + rec[2] + timestamp
                    return response

                else:
                    print("Need to renew")

     
       

        if mac in records:  #when getting discover, we check records  
            print("Found mac in records, so check timestamp for expire")  
            
        else:
            print("Not found, trying to add to records")
            if len(ip_addresses) != 0:                      #still have ip to use
                isotimestring = datetime.now().isoformat()    
                timestamp = datetime.fromisoformat(isotimestring)               
                secfromnow = timestamp + timedelta(seconds=60)

                newIP = ip_addresses.pop(0)

                newUser = (len(records), mac, newIP, secfromnow, False)
                
                records.append(newUser)
                
                #return an offer
                response = "OFFER " + mac + " " + newIP + " " + str(secfromnow)
                return response
            else:
                print("go through records to check for valid ip")
                

            
            
            

    elif request == "REQUEST":
        print("REQUEST MESSAGE")
        #respond wit hacknowledge

    elif request == "RELEASE":
        print("RELEASE MESSAGE")
        #get rid of ip?

    elif request == "RENEW":
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
