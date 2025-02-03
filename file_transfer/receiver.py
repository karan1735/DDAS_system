import socket
import os

# Define server address and port
SERVER_PORT = 5001
BUFFER_SIZE = 4096  # Buffer size for receiving data
SAVE_DIR = 'received_files'  # Directory to save the received files

def receive_file(ip_addr, file_to_request):
    # Create a socket object
    client_socket = socket.socket()

    print(f"[*] Attempting to connect to {ip_addr}:{SERVER_PORT}...")

    # Connect to the server
    client_socket.connect((ip_addr, SERVER_PORT))
    print(f"[+] Connected to {ip_addr}:{SERVER_PORT}")

    # Send the filename to the server
    print(f"[*] Requesting file: {file_to_request}")
    client_socket.send(file_to_request.encode())

    # Receive the metadata: filename and file size
    metadata = client_socket.recv(BUFFER_SIZE).decode().split('\n')
    if metadata[0].startswith('ERROR'):
        print(f"[-] Error from server: {metadata[0]}")
        client_socket.close()
        return

    server_filename = metadata[0]
    filesize = int(metadata[1])

    print(f"[+] Metadata received: Filename = {server_filename}, Filesize = {filesize} bytes")

    # Acknowledge metadata reception
    client_socket.send(b'ACK')
    print("[*] Sent acknowledgment to server.")

    # Ensure the directory exists
    if not os.path.exists(SAVE_DIR):
        print(f"[*] Save directory '{SAVE_DIR}' does not exist. Creating directory.")
        os.makedirs(SAVE_DIR)
    else:
        print(f"[*] Save directory '{SAVE_DIR}' exists.")

    # Define the path to save the received file
    save_path = os.path.join(SAVE_DIR, server_filename)
    print(f"[*] Saving file to: {save_path}")

    # Open the file in binary mode
    with open(save_path, 'wb') as file:
        bytes_received = 0
        print(f"[*] Starting file download...")
        while bytes_received < filesize:
            # Receive data from the server
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # File transmitting is done
                break
            # Write the received data to the file
            file.write(bytes_read)
            bytes_received += len(bytes_read)

    print(f"[+] File received successfully and saved as {save_path}. Total bytes received: {bytes_received}")

    # Close the client socket
    client_socket.close()
    print("[*] Connection closed.")

if __name__ == "__main__":
    receive_file(input("Ip Addr:"), input("Enter File Name:"))