import socket
import threading
import os
from datetime import datetime

# global variables
MAX_CLIENTS = 3 #limits the server to only allow 3 clients
clients = {} #stores all the active clients adds client name address and time of connection
client_count = 0 #number of clients 
lock = threading.Lock()  #thread safety
FILE_DIRECTORY = 'server_files'

"""
Create a function that handles the client connections
parameters: client_name, client_address, client_socket
client_address has their ip address and port number
client_name is the clients name
client_socket shows the connection between the server
and the client, sends and receives messages
"""
def handle_client(client_socket, client_name, client_address):
    global clients # make it global so it can be assccessed outside the function

    # find out connection time of the client
    with lock:
        clients[client_name] = {
            'address': client_address,
            'connected_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'disconnected_at': None
        }

    try:
        while True:
            message = client_socket.recv(1024).decode() # receives  from the client, a max of 1024 bytes
            if not message:
                break  # if no message is receieved the client disconnected

            #client commands
            if message.lower() == "exit":
                print(f"{client_name} Disconnected.")
                break  # Exit request

            elif message.lower() == "status":
                status_message = "\n".join(
                    [f"{name} - Connected: {info['connected_at']}, Disconnected: {info['disconnected_at'] or 'Active'}"
                     for name, info in clients.items()]
                )
                client_socket.send(status_message.encode()) #this sends a status response
            
            elif message.lower() == 'list': # list out the available files in a folder
               if os.path.exists(FILE_DIRECTORY):
                    files = os.listdir(FILE_DIRECTORY)
               else:
                   files = []
               if files:
                   files_list = "\n".join(files)
               else:
                   files_list = "No Files Available"
               client_socket.send(files_list.encode())

            elif message.lower().startswith("get "):  
               file_name = message[4:].strip()
               file_path = os.path.join(FILE_DIRECTORY, file_name)

               if os.path.exists(file_path) and os.path.isfile(file_path):
                    with open(file_path, "rb") as file:
                         while True:
                              chunk = file.read(1024)
                              if not chunk:
                                   break
                              client_socket.send(chunk)
                    client_socket.send(b"EOF")
               else:
                    error_message = f"ERROR: File '{file_name}' not found."
                    client_socket.send(error_message.encode())

            else:
                response = f"{message} ACK"
                client_socket.send(response.encode()) # this echos the messages back to the client with an acnkowledgement added

    except ConnectionResetError:
        print(f"{client_name} disconnected unexpectedly.") #for random discconections such as a force close

    finally:
        # find out the disconnection time then save it
        with lock:
            clients[client_name]['disconnected_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        client_socket.close()
        #print(f"{client_name} disconnected.") #closing the client socket i dont think we need this it doubles the message


def start_server():
    #Starts the server
    global client_count # make it global so it can be accessed

    if not os.path.exists(FILE_DIRECTORY):
        os.makedirs(FILE_DIRECTORY)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 3600)) #bind it to the host
    server_socket.listen(MAX_CLIENTS)

    print(f"Server is listening...")

    while True:
        if client_count < MAX_CLIENTS: # make sure that the client count does not exceed max clients
            client_socket, client_address = server_socket.accept()

            with lock:
                client_count += 1
                client_name = f"Client{client_count:02d}" #incrementing and alligning client names

            print(f"{client_name} connected from {client_address}")

            # start new threads for each client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_name, client_address))
            client_thread.start()
        else: #if the max amount of clients is reached disconnect them
            print("Max clients reached.")
            temp, _ = server_socket.accept()
            temp.send("Server is full. Try again later.".encode())
            temp.close()


if __name__ == '__main__':
    start_server()
