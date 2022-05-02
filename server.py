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
#{mac, tuple(record id, ip, timestamp, acked)}
_records = dict()

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
        print("server: LIST RECIEVED")
        response = "LIST " + str(_records)
        return response
    elif request == "DISCOVER":
        request, mac = parsed_message
        mac = mac.decode("utf8")
        print("server: DISCOVER RECIEVED")

        if mac in _records:
            print("server: User in records")
            isotimestring = datetime.now().isoformat()    
            timestamp = datetime.fromisoformat(isotimestring)
            old = _records[mac]

            if str(old[2]) > str(timestamp.time()):
                new = (old[0], old[1], old[2], True)
                _records[mac] = new
                print("server: Acknowledging user")
                response = "ACKNOWLEDGE  " + mac + " " + new[1] + " " + str(new[2])
                return response
                
            
        else:
            print("server: User not in records")
            if(len(ip_addresses) != 0):
                isotimestring = datetime.now().isoformat()
                timestamp = datetime.fromisoformat(isotimestring)
                secfromnow = timestamp + timedelta(seconds=60)

                newIP = ip_addresses.pop(0)               
                newUser = (len(_records), newIP, secfromnow, False)  #new user = (record #, server offer ip, timestamp, acked)
                    
                _records[mac] = newUser

                #return an offer
                print("server: Offering IP")                
                response = "OFFER " + mac + " " + newIP + " " + str(secfromnow)
                return response
            else:
                print("server: No more IP to allocate")


    elif request == "REQUEST":
        print("server: REQUEST RECIEVED")
        mac = parsed_message[1].decode("utf8")
        ip = parsed_message[2].decode("utf8")
        date = parsed_message[3].decode("utf8")
        time = parsed_message[4].decode("utf8")
        #respond with acknowledge
        rec = _records[mac]

        if ip in rec:
            isotimestring = datetime.now().isoformat()
            timestamp = datetime.fromisoformat(isotimestring)
            if(time > str(timestamp.time())):
                _records[mac] = (len(_records), ip, time, True)              

                response = "ACKNOWLEDGE " + mac + " " +_records[mac][1] + " " + str(_records[mac][2])
                return response
            else:
                response = "DECLINE"
                return response


    elif request == "RELEASE":
        print("server: RELEASE MESSAGE")
        mac = parsed_message[1].decode("utf8")
        ip = parsed_message[2].decode("utf8")
        time = parsed_message[3].decode("utf8")
     

        if mac in _records:
            ip_addresses.append(ip)         #since we popped the ip_addresses, lets push the ip back in
            del _records[mac]
            isotimestring = datetime.now().isoformat()
            timestamp = datetime.fromisoformat(isotimestring)
            _records[mac] = (len(_records), 0, timestamp, False)
            
            response = ""
            return response


    elif request == "RENEW":
        print("server: RENEW MESSAGE")
        mac = parsed_message[1].decode("utf8")
        ip = parsed_message[2].decode("utf8")
        time = parsed_message[3].decode("utf8")

        if mac in _records:
            isotimestring = datetime.now().isoformat()    
            timestamp = datetime.fromisoformat(isotimestring)
            secfromnow = timestamp + timedelta(seconds=60)

            renewUser = (len(_records), ip_addresses.pop(), secfromnow, True)
            _records[mac] = renewUser
            response = "ACKNOWLEDGE " + mac + " " +_records[mac][1] + " " + str(_records[mac][2])
            return response

        else:
            #check the ip pool for a new ip
            print("server: else")


# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Avoid TIME_WAIT socket lock [DO NOT REMOVE]
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", 9000))
print("server: DHCP Server running...")

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
