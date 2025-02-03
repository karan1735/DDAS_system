import customtkinter as ctk
from tkinter import messagebox
import sys
from mongo import connector
from uid_tracker import client as ip_finder
from file_transfer import receiver as file_receiver
from file_downloader import downloader
import threading
import json
from datetime import datetime

# Function to redirect print statements to the message box
class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(ctk.END, text)
        self.text_widget.see(ctk.END)  # Auto-scroll to the bottom

    def flush(self):
        pass  # Needed for Python's compatibility

# Function to save and update the download history
def save_download_history(entry):
    history_file = "download_history.json"
    
    try:
        # Load existing history
        with open(history_file, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"downloads": []}
    
    # Append new entry
    data["downloads"].append(entry)
    
    # Save back to file with pretty printing
    with open(history_file, "w") as file:
        json.dump(data, file, indent=4)

# Function to update the download history in the UI
def update_download_history(entry):
    # Create a new frame for each entry within the scrollable_frame
    entry_frame = ctk.CTkFrame(scrollable_frame, corner_radius=10)
    entry_frame.grid(row=len(scrollable_frame.grid_slaves()), column=0, padx=10, pady=5, sticky='ew')

    # Add labels and disabled input fields for each entry
    file_url_label = ctk.CTkLabel(entry_frame, text=f"File URL: {entry['file_url']}", font=("Helvetica", 16))
    file_url_label.grid(row=0, column=0, padx=5, pady=2, sticky='w')

    filename_label = ctk.CTkLabel(entry_frame, text=f"Filename: {entry['filename']}", font=("Helvetica", 16))
    filename_label.grid(row=1, column=0, padx=5, pady=2, sticky='w')

    method_label = ctk.CTkLabel(entry_frame, text=f"Method: {entry['method']}", font=("Helvetica", 16))
    method_label.grid(row=2, column=0, padx=5, pady=2, sticky='w')

    timestamp_label = ctk.CTkLabel(entry_frame, text=f"Timestamp: {entry['timestamp']}", font=("Helvetica", 16))
    timestamp_label.grid(row=3, column=0, padx=5, pady=2, sticky='w')

    status_label = ctk.CTkLabel(entry_frame, text=f"Status: {entry['status']}", font=("Helvetica", 16))
    status_label.grid(row=4, column=0, padx=5, pady=2, sticky='w')

    # Add a horizontal line (separator) below the entry to visually separate it
    separator = ctk.CTkFrame(scrollable_frame, height=2, fg_color="#CCCCCC")  # A thin gray line
    separator.grid(row=len(scrollable_frame.grid_slaves()), column=0, padx=5, pady=10, sticky='ew')

# Function to update progress bar
def update_progress(progress_var, value):
    progress_var.set(value)
    app.update_idletasks()


def choose_transfer_method():
    choice = ctk.StringVar()

    # Create a semi-transparent overlay
    overlay = ctk.CTkFrame(app, fg_color="gray10")
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Create the alert frame with a border
    alert_frame = ctk.CTkFrame(app, corner_radius=10, border_width=2, border_color="gray")
    alert_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Add danger symbol
    danger_symbol = ctk.CTkLabel(alert_frame, text="⚠", font=("Helvetica", 48), text_color="red")
    danger_symbol.pack(pady=(20, 10))

    label = ctk.CTkLabel(alert_frame, text="This file exists in the database.\nHow would you like to download it?", font=("Helvetica", 16))
    label.pack(pady=(0, 20), padx=20)

    def on_choice(method):
        choice.set(method)
        alert_frame.destroy()
        overlay.destroy()

    receive_button = ctk.CTkButton(alert_frame, text="Receive from Another Device", command=lambda: on_choice("Received from Other Device"))
    receive_button.pack(pady=10)

    direct_button = ctk.CTkButton(alert_frame, text="Direct URL Download", command=lambda: on_choice("Direct URL Download"))
    direct_button.pack(pady=10)

    app.wait_window(alert_frame)
    return choice.get()

# Function placeholder for the download process
def download_process(progress_var):
    entry = {
        "file_url": "",
        "filename": "",
        "method": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Failed"
    }
    
    file_url = url_input.get()
    if file_url:
        # Redirect stdout to capture the outputs
        sys.stdout = TextRedirector(debug_text)

        # Clear previous messages in the debug box
        debug_text.delete(1.0, ctk.END)

        try:
            # Initialize progress to 0
            update_progress(progress_var, 0)
            app.update_idletasks()  # Update the GUI immediately

            # Prepare entry for history
            entry["file_url"] = file_url

            # Step 1: Check if file URL exists in the database
            update_progress(progress_var, 0.2)
            retrieved_data = connector.find_data(file_url)

            if retrieved_data:
                entry["filename"] = retrieved_data["filename"]
                
                chosen_method = choose_transfer_method()
                entry["method"] = chosen_method

                if chosen_method == "Received from Other Device":
                    update_progress(progress_var, 0.5)
                    ip_found = ip_finder.get_ip(retrieved_data["user_id"])

                    if ip_found:
                        update_progress(progress_var, 0.8)
                        file_receiver.receive_file(ip_found, retrieved_data["filename"])
                        entry["status"] = "Completed"
                        update_progress(progress_var, 1.0)
                    else:
                        print(f"No IP address found for user_id: {retrieved_data['user_id']}")
                        entry["status"] = "Failed"
                else:
                    downloader.download(file_url)
                    update_progress(progress_var, 1.0)
                    print("File Downloaded from the server successfully!")
                    entry["status"] = "Completed"
            else:
                downloader.download(file_url)
                entry["filename"] = file_url.split('/')[-1]
                entry["method"] = "Direct URL Download"
                update_progress(progress_var, 1.0)
                print("File Downloaded from the server successfully!")
                entry["status"] = "Completed"
                
            # Save and update history
            save_download_history(entry)
            update_download_history(entry)

        except Exception as e:
            print(f"An error occurred: {e}")
            entry["status"] = "Failed"
            save_download_history(entry)
            update_download_history(entry)
        finally:
            url_input.delete(0, ctk.END)

        # Restore original stdout
        sys.stdout = sys.__stdout__

    else:
        messagebox.showwarning("Input Error", "Please enter a valid URL.")

def download_file():
    # Start download process in a new thread to prevent freezing
    progress_var.set(0)
    progress_bar.grid(row=3, column=0, pady=20, sticky='ew')
    download_thread = threading.Thread(target=download_process, args=(progress_var,))
    download_thread.start()

def load_download_history():
    history_file = "download_history.json"
    try:
        with open(history_file, "r") as file:
            data = json.load(file)
            for entry in data.get("downloads", []):
                update_download_history(entry)
    except FileNotFoundError:
        pass

def load_user_id():
    try:
        with open("user_id.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "User ID not found"

# Initialize the main window
app = ctk.CTk()
app.geometry("650x700")
app.resizable(False, False)
app.title("DDAS Application")

# Configure grid weights for the main window
app.grid_rowconfigure(0, weight=0)  # Header
app.grid_rowconfigure(1, weight=0)  # Tabview
app.grid_rowconfigure(2, weight=0)  # Progress bar
app.grid_rowconfigure(3, weight=1)  # Debug info

app.grid_columnconfigure(0, weight=1)

# Centering container frame
center_frame = ctk.CTkFrame(app, corner_radius=20)
center_frame.grid(row=0, column=0, padx=30, pady=30, sticky='nsew')

# Configure center_frame to expand and maintain proportions
center_frame.grid_rowconfigure(0, weight=0)  # Heading
center_frame.grid_rowconfigure(1, weight=0)  # Tabview
center_frame.grid_rowconfigure(2, weight=0)  # Progress bar
center_frame.grid_rowconfigure(3, weight=1)  # Debug info

center_frame.grid_columnconfigure(0, weight=1)

# Heading
heading_label = ctk.CTkLabel(center_frame, text="Data Download Duplication Alert System", font=("Helvetica", 26, "bold"))
heading_label.grid(row=0, column=0, pady=15)

# Tabview for different sections
tabview = ctk.CTkTabview(center_frame, width=800, height=500)
tabview.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')
tabview.add("Download")
tabview.add("History")

# User ID display
user_id = load_user_id()
user_id_label = ctk.CTkLabel(tabview.tab("Download"), text=f"User ID: {user_id}", font=("Helvetica", 16))
user_id_label.grid(row=0, column=0, padx=20, pady=10, sticky='ew')

# URL input section with placeholder
url_input = ctk.CTkEntry(tabview.tab("Download"), placeholder_text="Enter the URL", font=("Helvetica", 16), width=500)
url_input.grid(row=1, column=0, padx=20, pady=10, sticky='ew')

# Download button
download_button = ctk.CTkButton(tabview.tab("Download"), text="Start Download", command=download_file, font=("Helvetica", 16), width=200, height=40)
download_button.grid(row=2, column=0, pady=15)

# Progress bar for showing download progress
progress_var = ctk.DoubleVar()
progress_bar = ctk.CTkProgressBar(tabview.tab("Download"), variable=progress_var, width=500, height=20)
progress_bar.grid(row=3, column=0, pady=15, sticky='ew')
progress_bar.grid_remove()  # Hide progress bar initially

# Frame for Debug Info and message box
debug_frame = ctk.CTkFrame(tabview.tab("Download"))
debug_frame.grid(row=4, column=0, padx=20, pady=15, sticky='nsew')

# "Debug Info" label
debug_label = ctk.CTkLabel(debug_frame, text="Debug Info:", font=("Helvetica", 16, "bold"))
debug_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

# Message box for debug info
debug_text = ctk.CTkTextbox(debug_frame, wrap="word", font=("Helvetica", 14), width=500, height=250)
debug_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# Configure the frame to expand and fill the available space
debug_frame.grid_rowconfigure(1, weight=1)
debug_frame.grid_columnconfigure(0, weight=1)

# Frame for History Tab with Scrollbar
history_tab = tabview.tab("History")

# Configure history_tab to expand and fill available space
history_tab.grid_rowconfigure(0, weight=1)
history_tab.grid_columnconfigure(0, weight=1)

# Create a scrollable frame for the History Tab using CTkScrollableFrame
scrollable_frame = ctk.CTkScrollableFrame(history_tab, width=500, height=300)
scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

# Configure scrollable_frame to expand and fill available space
scrollable_frame.grid_rowconfigure(0, weight=1)
scrollable_frame.grid_columnconfigure(0, weight=1)

# Load history on app start
load_download_history()

# setting the default value for the url_input through the command line argument
if len(sys.argv) > 1:
    url_input.insert(0, sys.argv[1])
    download_file()

# Start the application
app.mainloop()