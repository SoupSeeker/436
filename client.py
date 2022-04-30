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

# LISTENING FOR RESPONSE
message, SERVER_IP = clientSocket.recvfrom(4096)
message = message.decode("utf8")
rec, mac, ip, date, time = message.split()  #timestamp shows up as (date) (time)

if rec == 'DECLINE':
    print("DECLINE RECIEVED")
    

elif rec == 'ACKNOWLEDGE':
    print("ACKNOWLEDGE RECIEVED")

elif rec == 'OFFER':
    print("OFFER RECIEVED") #when we get an offer, check mac, if good check timestamp
    if mac == MAC:
        
        isotimestring = datetime.now().isoformat()
        timestamp = datetime.fromisoformat(isotimestring)
        
        if(time > str(timestamp.time())):
            print("Valid")
            print(date, time)
            response = "REQUEST " + mac + " " + ip + " " + str(date) + " " + str(time)
            clientSocket.sendto(response.encode(), SERVER_IP)
        else: 
            print("Timestamp expired")

    else:
        print("Mac Mismatch")


elif rec == 'LIST':
    print("LIST RECIEVED")



def print_menu():
    print ('1 -- Option: Release' )
    print ('2 -- Option: Renew' )
    print ('3 -- Option: Quit' )
    
    option = int(input('Enter your choice: '))
    
    if option == 1:
        print('Handle option \ Option Release\'')
        message = "RELEASE " + mac + " " + ip + " " + time
        clientSocket.sendto(message.encode(), SERVER_IP)
    elif option == 2:
        print('Handle option \ Option Renew\'')
        message = "RENEW " +mac + " " + ip + " " + time
        clientSocket.sendto(message.encode(), SERVER_IP)
    elif option == 3:
        print('Handle option \ Option Quit\'')
        #quit
    else:
        print('Invalid option. please enter a number between 1 & 3')


    


