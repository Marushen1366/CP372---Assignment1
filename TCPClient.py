"""
-----------------------------------------------------------
TCPClient
---------------------------------------------------------
Author: Ashvinan Sivasambu
Id: 169021867
Email: siva1867
-----------------------------------------------------------
Author: Marushen Baskaran   
Id: 169019862
Email: bask9862@mylaurier.ca
-----------------------------------------------------------
"""


import socket

HOST = 'localhost' #hostname that refers to the machine the code is running on 
PORT = 3600 # port number for the server and client

def start_client(): 
    # starting the client and we are connecting to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT)) # creating a TCP socket and connecting it to the server at PORT 3600 on our local machine

    print("Connected to server. Type messages to send. Type 'status' to get active connections. Type 'exit' to disconnect.")

    try:
        while True: #using an infinite loop so that the client and server can send as many messages to each ohter as they want
            message = input("Enter message: ")
            client_socket.send(message.encode()) 

            if message.lower() == "exit": # gives the option for the user to disconnect from the server
                print("Disconnecting from server...")
                break 

            response = client_socket.recv(1024).decode()

            if message.lower().startswith("get "):
                file_name = message[4:].strip()
                if "ERROR" in response:
                    print(response)
                else:
                    with open(file_name, "wb") as file:
                        file.write(response.encode())
                    print(f"The File {file_name}.")
            else:
               print(f"Server: {response}") #receiving the server response at a maximum of 1024 bytes and printing it

    except ConnectionResetError:
        print("Server forcibly closed the connection.") # handle case for when the server disconnects randomly
    except ConnectionRefusedError: #handle case for when the server is not running or it is unreachavle 
        print("Could not connect to the server. Make sure the server is running.")
    finally:
        client_socket.close()
        print("Client socket closed.") #making sure the socket is closed properly befor ethe client exits the program


if __name__ == '__main__': 
    start_client() 