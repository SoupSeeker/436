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
        print("LIST MESSAGE")
      
    elif request == "DISCOVER":
        request, mac = parsed_message
        mac = mac.decode("utf8")

        if mac in _records:
            print("Found")
            isotimestring = datetime.now().isoformat()    
            timestamp = datetime.fromisoformat(isotimestring)
            old = _records[mac]
            oldTime = old[2]
            print(oldTime)
            
        else:
            print("Mac not in records")
            if(len(ip_addresses) != 0):
                print("```Offering IP```")
                isotimestring = datetime.now().isoformat()
                timestamp = datetime.fromisoformat(isotimestring)
                secfromnow = timestamp + timedelta(seconds=60)

                newIP = ip_addresses.pop(0)               
                newUser = (len(records), newIP, secfromnow, False)  #new user = (record #, server offer ip, timestamp, acked)
                    
                _records[mac] = newUser

                #return an offer
                response = "OFFER " + mac + " " + newIP + " " + str(secfromnow)
                return response
            else:
                print("```No more IP to allocate```")


        #for rec in records:
        #    if mac in rec:
        #        isotimestring = datetime.now().isoformat()    
         #       timestamp = datetime.fromisoformat(isotimestring)   
         #       old = rec[3]
          #      
           #     if old > timestamp:
            #        print("Still valid, just acknowledge")
             #       _rec = (rec[0], rec[1], rec[2], rec[3], True)       
              #      records.remove(rec)         
               ##    print(records) #delete later
                 #   response = "ACKNOWLEDGE " + " " + mac + " " + _rec[2] + " " + str(timestamp)
                  #  return response

                #else:
                 #   print("Need to renew")
            #else:
             #   print("Not found, trying to add to records")
              #  if len(ip_addresses) != 0:                      #still have ip to use
              #      isotimestring = datetime.now().isoformat()
               #     timestamp = datetime.fromisoformat(isotimestring)
                #    secfromnow = timestamp + timedelta(seconds=60)

                 #   newIP = ip_addresses.pop(0)

                  #  newUser = (len(records), mac, newIP, secfromnow, False)
                    
                   # records.append(newUser)
                    
                    #return an offer
                   # response = "OFFER " + mac + " " + newIP + " " + str(secfromnow)
                    #return response


    elif request == "REQUEST":
        print("REQUEST MESSAGE")
        #respond with acknowledge
        

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
