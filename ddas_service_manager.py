import threading
from uid_gen import uid_gen
from file_transfer import sender as file_sender
from uid_tracker import server as uid_server
from Extenstion import extension_api

def start_file_sender():
    print("Starting File Sender...")
    file_sender.start_server()

def start_uid_server():
    print("Starting UID Server...")
    uid_server.start_server()
    
def start_extension_api():
    print("Starting Extension API...")
    extension_api.app.run(port=5003)

def start():
    # Generate UID
    uid_gen.generate()

    # Start each server in a separate thread
    file_sender_thread = threading.Thread(target=start_file_sender)
    uid_server_thread = threading.Thread(target=start_uid_server)
    extension_api_thread = threading.Thread(target=start_extension_api)

    file_sender_thread.start()
    uid_server_thread.start()
    extension_api_thread.start()

if __name__ == "__main__":
    start()