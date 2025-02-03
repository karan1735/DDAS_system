from pymongo import MongoClient
import requests
from urllib.parse import urlparse, unquote

# MongoDB connection URL
db_url = "mongodb+srv://user1:karan@cluster1.bozbp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"

def get_file_info(url):
    print(f"Starting to get file info for URL: {url}")
    try:
        # Send a HEAD request to get metadata without downloading the file
        response = requests.head(url, allow_redirects=True)
        print(f"HEAD request sent to {url}. Status Code: {response.status_code}")
        
        # Check if the request was successful
        if response.status_code == 200:
            # Extract relevant information from the headers
            content_length = response.headers.get('Content-Length', 'Unknown')
            etag = response.headers.get('ETag', 'Unknown')
            content_disposition = response.headers.get('Content-Disposition', 'Unknown')
            final_url = response.url

            print(f"Response headers: Content-Length={content_length}, ETag={etag}, Content-Disposition={content_disposition}")

            # Extract filename from Content-Disposition header if available
            filename = 'Unknown'
            if content_disposition and ('attachment' in content_disposition or 'inline' in content_disposition):
                filename = content_disposition.split('filename=')[-1].strip('"').strip("'")
                filename = unquote(filename)  # Decode URL-encoded filename

            # If filename is still 'Unknown', infer it from the URL path
            if filename == 'Unknown':
                parsed_url = urlparse(final_url)
                filename = parsed_url.path.split('/')[-1]
                filename = unquote(filename)  # Decode URL-encoded filename

            # Return metadata as a dictionary
            return {
                'url': final_url,
                'filename': filename,
                'content_length': content_length,
                'etag': etag
            }

        else:
            print(f"Failed to retrieve information. HTTP Status Code: {response.status_code}")
            return None

    except requests.RequestException as e:
        print(f"An error occurred while fetching file info: {e}")
        return None

def get_user_id():
    """
    Reads the user ID from the user_id.txt file.
    """
    print("Attempting to read user ID from file.")
    try:
        with open("user_id.txt", "r") as f:
            user_id = f.read().strip()  # Read and remove any extra whitespace
        print(f"User ID retrieved: {user_id}")
        return user_id
    except Exception as e:
        print(f"Error reading user ID: {e}")
        return None

def check_if_file_exists(collection, file_info):
    """
    Check and returns the details if the file already exists in the collection.
    """
    print(f"Checking if file already exists in the database for file info: {file_info}")
    try:
        # Check for a document with the same URL, filename, ETag, and content length
        existing_file = collection.find_one({
            'url': file_info['url'],            # Check by URL
            'filename': file_info['filename'],  # Check by filename
            'etag': file_info['etag'],          # Check by ETag
            'content_length': file_info['content_length']  # Check by content length
        })

        if existing_file:
            print("Alert: This file is already present in the database.")
            return existing_file  # File exists
        else:
            print("This is a new file. Downloading it from the link.")
            return None  # File does not exist
    except Exception as e:
        print(f"Error while checking file existence: {e}")
        return None

def find_data(url):
    print(f"Starting process to find data for URL: {url}")

    # Get file information
    file_info = get_file_info(url)
    print(f"File info retrieved: {file_info}")

    # Connect to MongoDB and check if file exists
    if file_info:
        # Step 1: Get the user ID
        user_id = get_user_id()
        if not user_id:
            print("User ID is missing. Cannot proceed.")
        else:
            # Step 2: Create a MongoDB client
            print("Connecting to MongoDB...")
            client = MongoClient(db_url)

            retrived_data = None

            try:
                # Step 3: Connect to the database
                db = client.get_database('DDAS')
                print(f"Connected to the database 'DDAS'.")

                # Step 4: Define a collection
                file_metadata_collection = db['FileMetadata']
                print(f"Using collection 'FileMetadata'.")

                # Step 5: Check if file already exists
                retrived_data = check_if_file_exists(file_metadata_collection, file_info)
                
                if not retrived_data:
                    # Step 6: Add the user ID to the file info and save it to the database
                    print("File is new. Saving to the database...")
                    file_info['user_id'] = user_id
                    result = file_metadata_collection.insert_one(file_info)
                    print(f"Document saved with ID: {result.inserted_id}")

            except Exception as e:
                print(f"Error connecting to the DB or saving document: {e}")

            finally:
                # Close the connection
                client.close()
                print("MongoDB connection closed.")
                return retrived_data