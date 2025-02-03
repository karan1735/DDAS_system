import socket
import os
import uuid

# Get the user ID from a file or generate a new one
user_id_file = 'user_id.txt'

if os.path.exists(user_id_file):
    with open(user_id_file, 'r') as file:
        user_id = file.read()
else:
    user_id = str(uuid.uuid4())
    with open(user_id_file, 'w') as file:
        file.write(user_id)

# Get the IP address of the system
def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

# Function to listen for incoming broadcasts
def listen_for_user_id():
    # UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 50000))  # Bind to port 50000 and listen on all interfaces
    
    while True:
        print("Listening for broadcasts...")
        data, addr = sock.recvfrom(1024)  # Receive up to 1024 bytes
        received_user_id = data.decode()

        print(f"Received user ID {received_user_id} from {addr}")

        # Check if the received user ID matches the current system's user ID
        if received_user_id == user_id:
            # Send the system's IP address back to the requester
            ip_address = get_ip_address()
            sock.sendto(ip_address.encode(), addr)
            print(f"User ID match found! Sent IP address {ip_address}")

def start_server():
    print("Starting UID server...")
    # Start listening for user ID broadcasts
    listen_for_user_id()
