import socket
import os

# Define server address and port
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 5001
BUFFER_SIZE = 4096  # Buffer size for sending data

def get_local_ip():
    # Get the local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def send_file(client_socket):
    try:
        # Receive the requested filename from the client
        requested_filename = client_socket.recv(BUFFER_SIZE).decode()

        # Check if the file exists
        if not os.path.isfile(requested_filename):
            client_socket.send(b'ERROR: File not found')
            print(f"File not found: {requested_filename}")
            return

        # Send the filename and file size to the client
        filesize = os.path.getsize(requested_filename)
        client_socket.sendall(f'{requested_filename}\n{filesize}'.encode())

        # Wait for the client to acknowledge before sending file data
        client_socket.recv(BUFFER_SIZE)

        # Open the file in binary mode
        with open(requested_filename, 'rb') as file:
            while True:
                # Read the file in chunks
                bytes_read = file.read(BUFFER_SIZE)
                if not bytes_read:
                    # File transmitting is done
                    break
                # Send the chunk to the client
                client_socket.sendall(bytes_read)
        print(f"[+] File {requested_filename} sent successfully.")
    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        # Ensure everything is closed and cleared
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        print("[*] Client connection closed.")

def start_server():
    server_socket = None
    try:
        # Create a socket object
        server_socket = socket.socket()

        # Bind the socket to the server address
        server_socket.bind((SERVER_HOST, SERVER_PORT))

        # Listen for incoming connections
        server_socket.listen(5)
        print(f"[*] Server listening as {SERVER_HOST}:{SERVER_PORT}")

        # Print local IP address
        local_ip = get_local_ip()
        print(f"Server IP Address: {local_ip}")

        while True:
            # Accept connection
            client_socket, address = server_socket.accept()
            print(f"[+] {address} connected.")

            # Handle file request
            send_file(client_socket)

    except Exception as e:
        print(f"[-] Server Error: {e}")
    finally:
        # Ensure the server socket is properly closed
        if server_socket:
            server_socket.close()
            print("[*] Server socket closed.")
