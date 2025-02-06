import socket
import threading
from datetime import datetime

# global variables
MAX_CLIENTS = 3 #limits the server to only allow 3 clients
clients = {} #stores all the active clients adds client name address and time of connection
client_count = 0 #number of clients 
lock = threading.Lock()  #thread safety
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
            data = client_socket.recv(1024).decode() # receives data from the client, a max of 1024 bytes
            if not data:
                break  # if no data is receieved the client disconnected

            #client commands
            if data.lower() == "exit":
                print(f"{client_name} Disconnected.")
                break  # Exit request

            elif data.lower() == "status":
                status_message = "\n".join(
                    [f"{name} - Connected: {info['connected_at']}, Disconnected: {info['disconnected_at'] or 'Active'}"
                     for name, info in clients.items()]
                )
                client_socket.send(status_message.encode()) #this sends a status response

            else:
                response = f"{data} ACK"
                client_socket.send(response.encode()) # this echos the messages back to the client with an acnkowledgement added

    except ConnectionResetError:
        print(f"{client_name} disconnected unexpectedly.") #for random discconections such as a force close

    finally:
        # find out the disconnection time then save it
        with lock:
            clients[client_name]['disconnected_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        client_socket.close()
        print(f"{client_name} disconnected.") #closing the client socket


def start_server():
    #Starts the server
    global client_count # make it global so it can be accessed
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 3500)) #bind it to the host
    server_socket.listen(MAX_CLIENTS)

    print(f"Server is running on {'localhost'}:{3500}...")

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
            client_socket, _ = server_socket.accept()
            client_socket.send("Server is full. Try again later.".encode())
            client_socket.close()


if __name__ == '__main__':
    start_server()
