#!/usr/bin/env python3
import uuid
import socket
from datetime import datetime

# Time operations in python
# isotimestring = datetime.now().isoformat()
# timestamp = datetime.fromisoformat(isotimestring)

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending DISCOVER message
message = "DISCOVER " + MAC
clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

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


def print_menu(mac, ip, time):
    print ('client: 1 -- Option: Release' )
    print ('client: 2 -- Option: Renew' )
    print ('client: 3 -- Option: Quit' )
    
    option = int(input('Enter your choice: '))
    
    if option == 1:
        print('client: Release')
        message = "RELEASE " + mac + " " + ip + " " + time
        clientSocket.sendto(message.encode(), SERVER_IP)
    elif option == 2:
        print('client: Renew')
        message = "RENEW " +mac + " " + ip + " " + time
        clientSocket.sendto(message.encode(), SERVER_IP)
    elif option == 3:
        print('client: Quit')
        quit()
    else:
        print('client: Invalid option. please enter a number between 1 & 3')


# LISTENING FOR RESPONSE

while True:
    message, SERVER_IP = clientSocket.recvfrom(4096)  

    message = message.decode("utf8")
    parsed = parse_message(message)
    #req, mac, ip, date, time = message.split()  #timestamp shows up as (date) (time)
    req = parsed[0]

    if req == 'DECLINE':
        print("client: DECLINE RECIEVED")
        print("client: TRY AGAIN")
        quit()
        

    elif req == 'ACKNOWLEDGE':
        print("client: ACKNOWLEDGE RECIEVED") #send back a request
        mac = parsed[1]
        ip = parsed[2]
        time = parsed[3]
        
        if mac == MAC:
            print("\nclient: Connected to device with Mac: " + mac + ", IP Address: " + ip + ", Timestamp: " + time)
        
        while True:
            print_menu(mac, ip, time)
            message, SERVER_IP = clientSocket.recvfrom(4096) 
            if message: 
                message = message.decode("utf8")
                parsed = parse_message(message)
                req = parsed[0]
                mac = parsed[1]
                ip = parsed[2]
                time = parsed[4]
                if req == 'ACKNOWLEDGE':
                    print("\nclient: Connected to device with Mac: " + mac + ", IP Address: " + ip + ", Timestamp: " + time)
            


        #break


    elif req == 'OFFER':
        print("client: OFFER RECIEVED") #when we get an offer, check mac, if good check timestamp
        mac = parsed[1]
        ip = parsed[2]
        date = parsed[3]
        time = parsed[4]

        if mac == MAC:
            
            isotimestring = datetime.now().isoformat()
            timestamp = datetime.fromisoformat(isotimestring)
            
            if(time > str(timestamp.time())):
                print("client: REQUESTING IP")
                response = "REQUEST " + mac + " " + ip + " " + str(date) + " " + str(time)
                clientSocket.sendto(response.encode(), SERVER_IP)
            else: 
                print("client: Timestamp expired")

        else:
            print("client: Mac Mismatch")


    elif req == 'LIST':
        print("client: LIST RECIEVED")







    


