import os
import uuid

def generate():
    # Define the file where the user ID will be saved
    user_id_file = 'user_id.txt'

    # Check if the file already exists
    if os.path.exists(user_id_file):
        # If the file exists, read the ID
        with open(user_id_file, 'r') as file:
            user_id = file.read()
            print(f"User ID already exists: {user_id}")
    else:
        # If the file doesn't exist, generate a new unique ID
        user_id = str(uuid.uuid4())  # Generates a random unique identifier
        with open(user_id_file, 'w') as file:
            file.write(user_id)
        print(f"New User ID generated: {user_id}")
