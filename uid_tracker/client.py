import socket

def get_ip(user_id):
    # UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Set socket to broadcast mode
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Broadcast to port 50000
    broadcast_address = ('<broadcast>', 50000)

    print(f"Broadcasting user ID {user_id} to the network...")
    
    # Send the user ID
    sock.sendto(user_id.encode(), broadcast_address)

    # Wait for a response
    sock.settimeout(5)  # Timeout after 5 seconds
    try:
        data, addr = sock.recvfrom(1024)  # Wait for a response (IP address)
        print(f"Received IP address {data.decode()} from {addr}")
    except socket.timeout:
        print("No response received. User ID not found on the network.")
    finally:
        return data.decode()
