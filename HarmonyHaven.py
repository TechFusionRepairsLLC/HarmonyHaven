import os
import glob
import hashlib
import pygame
from mutagen.id3 import ID3
from tkinter import *
from tkinter import filedialog, messagebox, colorchooser
from tkinter import ttk, PhotoImage
import tkinter as tk
from PIL import Image, ImageTk
from pydub import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from database_manager import create_music_table, insert_into_db, search_for_song, find_duplicates
import sys

# Check if ffmpeg is installed for Pydub
pygame.mixer.init()

# Function to get the resource path when bundled with PyInstaller
def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

icon_path = resource_path("HarmonyHaven.ico")
logo_path = resource_path("HarmonyHavenlogo.png")
qr_path = resource_path("TFRLLC_QRCODE.png")

# Create the main window using Tkinter
root = Tk()
root.title("HarmonyHaven by TechFusion Repairs LLC")
root.geometry("800x1000")
if getattr(sys, 'frozen', False):
    # If the application is running as a bundled executable
    base_path = sys._MEIPASS
else:
    # If the application is running as a script
    base_path = os.path.dirname(os.path.abspath(__file__))

# Set the icon
icon_path = resource_path('HarmonyHaven.ico')
try:
    root.iconbitmap(icon_path)
except Exception as e:
    print(f"Failed to set icon: {e}")

# Copyright notice at the bottom
copyright_label = Label(root, text="© 2024 TechFusion Repairs LLC. All rights reserved.", font=("Arial", 10), justify='center')
copyright_label.pack(side='bottom', pady=5)

# Global variableas
music_files = []
current_playlist = []
current_song = None
root_directory = None
bg_color = "white"
bg_image = None

# Function to log messages to the log window
def log_message(log_text_widget, message):
    log_text_widget.insert(END, message + "\n")
    log_text_widget.see(END)

# Function to change background color
def change_bg_color():
    global bg_color
    color = colorchooser.askcolor()[1]
    if color:
        bg_color = color
        root.config(bg=bg_color)

# Function to set a background image
def set_bg_image():
    global bg_image
    file_path = filedialog.askopenfilename(title="Select Background Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        bg_image = Image.open(file_path)
        bg_image = ImageTk.PhotoImage(bg_image)
        canvas = Canvas(root, width=800, height=600)
        canvas.create_image(0, 0, anchor=NW, image=bg_image)
        canvas.pack(fill="both", expand=True)

# Function to display License Information
def show_license_info():
    messagebox.showinfo("License", "HarmonyHaven is licensed under TechFusion Repairs LLC.")

# Function to display contact information
def show_contact_info():
    messagebox.showinfo("Contact", "For support, contact:\nEmail: support@techfusionrepairsllc.com or TechFusionRepairsLLC@gmail.com\nPhone:(940) 808-5105\nWebsite: www.TechFusionRepairsLLC.com")

# Function to select a directory for scanning music files
def select_directory(log_text_widget):
    global root_directory
    root_directory = filedialog.askdirectory()
    if root_directory:
        log_message(log_text_widget, f"Scanning directory: {root_directory}")
        scan_music_files(root_directory, log_text_widget)

# Scan for music files in the selected directory
def scan_music_files(directory, log_text_widget):
    global music_files
    music_files = []
    extensions = ['.mp3', '.flac', '.wav', '.m4a']
    for ext in extensions:
        music_files.extend(glob.glob(os.path.join(directory, '**', f'*{ext}'), recursive=True))

    if music_files:
        log_message(log_text_widget, f"Found {len(music_files)} music files.")
        update_song_list()
    else:
        log_message(log_text_widget, "No music files found in the selected directory.")

# Calculate MD5 hash to find duplicates
def calculate_hash(file_path, chunk_size=8192):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Find duplicate music files
def find_duplicates(log_text_widget):
    if not music_files:
        log_message(log_text_widget, "No music files found to check for duplicates.")
        return

    hashes = {}
    duplicates = []
    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(calculate_hash, file_path): file_path for file_path in music_files}
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                file_hash = future.result()
                if file_hash in hashes:
                    duplicates.append((file_path, hashes[file_hash]))
                else:
                    hashes[file_hash] = file_path
            except Exception as exc:
                log_message(log_text_widget, f"Error hashing file {file_path}: {exc}")

    if duplicates:
        log_message(log_text_widget, f"Found {len(duplicates)} duplicate files.")
        remove_duplicates(duplicates, log_text_widget)
    else:
        log_message(log_text_widget, "No duplicate music files found.")

# Function to remove duplicates
def remove_duplicates(duplicates, log_text_widget):
    for dup in duplicates:
        os.remove(dup[0])
        log_message(log_text_widget, f"Deleted duplicate file: {dup[0]}")
    log_message(log_text_widget, "Duplicate files have been deleted.")

def delete_empty_folders(log_text_widget):
    if not root_directory:
        log_message(log_text_widget, "Please scan a directory first.")
        return

    empty_folders = []
    for folder, subfolders, files in os.walk(root_directory, topdown=False):
        if not subfolders and not files:
            empty_folders.append(folder)
            os.rmdir(folder)

    if empty_folders:
        log_message(log_text_widget, f"Deleted {len(empty_folders)} empty folder(s).")
        for folder in empty_folders:
            log_message(log_text_widget, f"Deleted empty folder: {folder}")
    else:
        log_message(log_text_widget, "No empty folders found.")

# Play selected music file
def play_music(file_path):
    global current_song
    current_song = file_path
    if os.path.exists(file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
    else:
        messagebox.showwarning("File Not Found", f"File '{file_path}' does not exist.")

# Pause playback
def pause_music():
    pygame.mixer.music.pause()

# Stop playback
def stop_music():
    pygame.mixer.music.stop()

# Set volume
def set_volume(volume_level):
    # Convert volume_level to a float
    volume_level = float(volume_level)
    # Set the volume using pygame
    pygame.mixer.music.set_volume(volume_level / 100.0)

# Function to play the selected song from the listbox
def play_selected_song():
    selection = song_listbox.curselection()
    if selection:
        selected_song = song_listbox.get(selection[0])
        play_music(selected_song)

# Search for music files by name
def search_for_song(log_text_widget):
    song_name = song_search_entry.get()
    found_files = []
    extensions = ['.mp3', '.flac', '.wav', '.m4a']
    for ext in extensions:
        found_files.extend(glob.glob(os.path.join(root_directory, '**', f'*{song_name}*{ext}'), recursive=True))

    if found_files:
        log_message(log_text_widget, f"Found {len(found_files)} file(s) matching '{song_name}'. Locations: {', '.join(found_files)}")
    else:
        log_message(log_text_widget, f"No files found matching '{song_name}'.")

# Update the song listbox with the scanned files
def update_song_list():
    song_listbox.delete(0, END)
    for file in music_files:
        song_listbox.insert(END, file)

# Function to get all available ID3 tags from the first music file
def get_id3_tags():
    if music_files:
        audio = ID3(music_files[0])
        tags = {}
        for tag in audio.keys():
            frames = audio.getall(tag)
            if frames:
                # Safely access the tag values
                if hasattr(frames[0], 'text') and frames[0].text:
                    tags[tag] = frames[0].text[0]
                elif hasattr(frames[0], 'data'):
                    tags[tag] = "Binary Data"  # Handle binary data if needed
                else:
                    tags[tag] = "Unknown"
            else:
                tags[tag] = "Unknown"  # Tag is present but has no frames
        return tags
    return {}

# Function to organize music by ID3 tags
def organize_music_by_id3(log_text_widget):
    if not music_files:
        log_message(log_text_widget, "No music files found to organize.")
        return

    id3_tags = get_id3_tags()
    if not id3_tags:
        log_message(log_text_widget, "No ID3 tags found.")
        return

    # Create a new window for tag selection
    organize_window = Toplevel(root)
    organize_window.title("Select ID3 Tags for Organizing")
    
    # Selection for primary folder tag
    Label(organize_window, text="Select Primary Folder Tag:").pack()
    primary_tag_var = StringVar()
    primary_tag_menu = OptionMenu(organize_window, primary_tag_var, *id3_tags.keys())
    primary_tag_menu.pack(pady=5)

    # Selection for subfolder tag
    Label(organize_window, text="Select Subfolder Tag:").pack()
    subfolder_tag_var = StringVar()
    subfolder_tag_menu = OptionMenu(organize_window, subfolder_tag_var, *id3_tags.keys())
    subfolder_tag_menu.pack(pady=5)

    # Sort button
    sort_button = Button(organize_window, text="Sort", command=lambda: sort_music_by_id3(primary_tag_var.get(), subfolder_tag_var.get(), log_text_widget, organize_window))
    sort_button.pack(pady=5)

# Function to sort music files by selected ID3 tags
def sort_music_by_id3(primary_tag, subfolder_tag, log_text_widget, window):
    organized_folder = filedialog.askdirectory(title="Select a Folder for Organizing Music")
    if organized_folder:
        for file in music_files:
            try:
                audio = ID3(file)
                primary_value = audio.getall(primary_tag)[0].text[0] if audio.getall(primary_tag) else "Unknown"
                subfolder_value = audio.getall(subfolder_tag)[0].text[0] if audio.getall(subfolder_tag) else "Unknown"

                new_folder = os.path.join(organized_folder, primary_value, subfolder_value)
                os.makedirs(new_folder, exist_ok=True)
                os.rename(file, os.path.join(new_folder, os.path.basename(file)))
                log_message(log_text_widget, f"Moved {file} to {new_folder}")
            except Exception as e:
                log_message(log_text_widget, f"Error organizing {file}: {e}")
    
    window.destroy()

# Function to allow adding subfolders for organizing
def add_subfolder_for_organizing(log_text_widget):
    subfolder = filedialog.askdirectory(title="Select Subfolder")
    if subfolder:
        log_message(log_text_widget, f"Subfolder added for organizing: {subfolder}")
        scan_music_files(subfolder, log_text_widget)

# Create tabs using ttk.Notebook
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Tab 1: File Operations (Scan, Duplicate, Logs)
tab_file_ops = Frame(notebook)
notebook.add(tab_file_ops, text="File Operations")

HarmonyHavenlogo_image_path = resource_path("HarmonyHavenlogo.png")
try:
    # Load the original image
    HarmonyHavenlogo_image = PhotoImage(file=HarmonyHavenlogo_image_path)
    
    # Resize the image (for example, to half its size)
    HarmonyHavenlogo_image = HarmonyHavenlogo_image.subsample(2)  # Adjust the argument to scale down
    
    # Create a label with the resized image
    HarmonyHavenlogo_label = Label(tab_file_ops, image=HarmonyHavenlogo_image)
    HarmonyHavenlogo_label.pack(pady=10)
except Exception as e:
    print(f"Failed to load HarmonyHaven logo image: {e}")

# Log window for file operations
log_text = Text(tab_file_ops, height=10, state=NORMAL)
log_text.pack(padx=10, pady=10, fill=X)


# Buttons for scanning and finding duplicates
scan_button = Button(tab_file_ops, text="Scan Directory", command=lambda: select_directory(log_text))
scan_button.pack(pady=5)

find_duplicates_button = Button(tab_file_ops, text="Find Duplicates", command=lambda: find_duplicates(log_text))
find_duplicates_button.pack(pady=5)

# button to trigger the delete empty folders function
delete_empty_folders_button = Button(tab_file_ops, text="Delete Empty Folders", command=lambda: delete_empty_folders(log_text))
delete_empty_folders_button.pack(pady=5)

# Tab 2: Music Playback
tab_playback = Frame(notebook)
notebook.add(tab_playback, text="Music Playback")

# Listbox to display the songs
song_listbox = Listbox(tab_playback, height=10)
song_listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)

# Playback control buttons
play_button = Button(tab_playback, text="Play Selected Song", command=play_selected_song)
play_button.pack(pady=5)

pause_button = Button(tab_playback, text="Pause", command=pause_music)
pause_button.pack(pady=5)

stop_button = Button(tab_playback, text="Stop", command=stop_music)
stop_button.pack(pady=5)

# Volume control
volume_scale = Scale(tab_playback, from_=0, to=100, label="Volume", orient=HORIZONTAL, command=set_volume)
volume_scale.set(50)  # Set default volume to 50%
volume_scale.pack(pady=5)

# Tab 3: Search Music
tab_search = Frame(notebook)
notebook.add(tab_search, text="Search Music")

# Search bar for finding a song
search_frame = Frame(tab_search)
search_frame.pack(pady=10)
song_search_entry = Entry(search_frame, width=50)
song_search_entry.pack(side=LEFT, padx=10)
search_button = Button(search_frame, text="Search Song", command=lambda: search_for_song(log_text))
search_button.pack(side=LEFT)


# Tab 4: Settings
tab_settings = Frame(notebook)
notebook.add(tab_settings, text="Settings")

# Settings section: Change background color and image
change_bg_button = Button(tab_settings, text="Change Background Color", command=change_bg_color)
change_bg_button.pack(pady=5)

set_bg_image_button = Button(tab_settings, text="Set Background Image", command=set_bg_image)
set_bg_image_button.pack(pady=5)

license_button = Button(tab_settings, text="License", command=show_license_info)
license_button.pack(pady=5)

# Adding a scrollable box for How To Use This App
how_to_use_frame = Frame(tab_settings)
how_to_use_frame.pack(pady=10, padx=10, fill=BOTH, expand=True)

how_to_use_textbox = Text(how_to_use_frame, wrap=WORD, height=20, width=80)
how_to_use_textbox.pack(side=LEFT, fill=BOTH, expand=True)

# Adding a scrollbar to the text box
scrollbar = Scrollbar(how_to_use_frame, command=how_to_use_textbox.yview)
scrollbar.pack(side=RIGHT, fill=Y)

how_to_use_textbox.config(yscrollcommand=scrollbar.set)

# Inserting How To Use This App text into the textbox
how_to_use_text = """
Welcome to HarmonyHaven, your ultimate music file management app! Follow these simple steps to get started with organizing, playing, and managing your music collection.

1. Scanning Music Files
   - Select a Directory: Navigate to the File Operations tab and click on Scan Directory. Choose the folder containing your music files.
   - View Results: The app will scan the selected directory and log the number of music files found in the log window.

2. Finding Duplicate Files
   - After scanning, click the Find Duplicates button. The app will identify duplicate files based on their MD5 hash and log the results.
   - If duplicates are found, you can delete them directly through the log messages.

3. Playing Music
   - Switch to the Music Playback tab.
   - Select a song from the list and click Play Selected Song to start playback.
   - Use the Pause and Stop buttons to control playback.
   - Adjust the volume using the volume slider.

4. Searching for Songs
   - In the Search Music tab, enter a song name in the search bar and click Search Song.
   - The app will display the number of matching files and their locations in the log window.

5. Organizing Music by ID3 Tags
   - Go to the Organize Music tab and click on Organize Music by ID3.
   - Select a primary folder tag and a subfolder tag from the dropdown menus that appear.
   - Choose a folder to organize your music, and the app will move files into the corresponding subfolders based on the selected tags.

6. Adding Subfolders for Organizing
   - Click on Add Subfolder for Organizing to select a folder for additional music files. The app will scan the new folder and log the results.

7. Changing App Settings
   - Navigate to the Settings tab to change the background color or set a background image for the app.
   - Access the How To Use and License information from the Settings tab as well.

8. Contacting Support
   - For support, click on the Contact tab, and reach out via the provided email address.

9. Logging Messages
   - Throughout the app, all actions and results will be logged in the log window at the bottom of the interface. Keep an eye on this area for important messages and status updates.
"""

how_to_use_textbox.insert(END, how_to_use_text)
how_to_use_textbox.config(state=DISABLED)  # Make the text read-only

# Tab 5: Contact
tab_contact = Frame(notebook)
notebook.add(tab_contact, text="Contact")

contact_button = Button(tab_contact, text="Contact Us", command=show_contact_info)
contact_button.pack(pady=5)

Label(tab_contact, text="For support, please reach out to us:", font=("Arial", 12)).pack(pady=5)

# Display email information
Label(tab_contact, text="Email: support@techfusionrepairsllc.com", font=("Arial", 12), fg="blue").pack(pady=5)
Label(tab_contact, text="Or: TechFusionRepairsLLC@gmail.com", font=("Arial", 12), fg="blue").pack(pady=5)

# Display phone number information
Label(tab_contact, text="Phone: (940) 808-5105", font=("Arial", 12), fg="blue").pack(pady=5)

# Display website information
Label(tab_contact, text="Website: www.TechFusionRepairsLLC.com", font=("Arial", 12), fg="blue").pack(pady=5)

# Adding additional notes for users
Label(tab_contact, text="We aim to respond to all inquiries within 24-48 hours.", font=("Arial", 10, "italic"), fg="green").pack(pady=10)

# Donate png and website

Label(tab_contact, text="Donations are not required but greatly appreciated as they help support the project.", font=("Arial", 12, "italic"), fg="red").pack(pady=10)
paypal_link = tk.Label(tab_contact, text="https://www.paypal.com/donate/?hosted_button_id=CESA5GQALY386", 
                       font=("Arial", 12), fg="blue", cursor="hand2")
paypal_link.pack(pady=5)

# Function to open the PayPal link when clicked
def open_paypal(event):
    import webbrowser
    webbrowser.open(paypal_link.cget("text"))

# Bind the label to open the link when clicked
paypal_link.bind("<Button-1>", open_paypal)

# Load the QR code image
qr_image_path = resource_path("TFRLLC_QRCODE.png")
try:
    qr_image = PhotoImage(file=qr_image_path)
    qr_label = Label(tab_contact, image=qr_image)
    qr_label.pack(pady=10)
except Exception as e:
    print(f"Failed to load QR image: {e}")

# Tab 6: Organize Music
tab_organize = Frame(notebook)
notebook.add(tab_organize, text="Organize Music")

organize_button = Button(tab_organize, text="Organize Music by ID3", command=lambda: organize_music_by_id3(log_text))
organize_button.pack(pady=5)

add_subfolder_button = Button(tab_organize, text="Add Subfolder for Organizing", command=lambda: add_subfolder_for_organizing(log_text))
add_subfolder_button.pack(pady=5)

details_frame = Frame(tab_organize)
details_frame.pack(pady=10, padx=10, fill=BOTH, expand=True)

details_textbox = Text(details_frame, wrap=WORD, height=20, width=80)
details_textbox.pack(side=LEFT, fill=BOTH, expand=True)

# Adding a scrollbar to the text box
scrollbar = Scrollbar(details_frame, command=details_textbox.yview)
scrollbar.pack(side=RIGHT, fill=Y)
details_text = """Break down of what each ID3 tag means:

1. TIT2 (Title/Song Name/Content Description)
Description: Contains the title of the audio or song.
Example: "Bohemian Rhapsody"

2. TPE1 (Lead Artist/Performer/Soloist/Group)
Description: Represents the main artist or performer of the audio file.
Example: "Queen"

3. TCON (Content Type/Genre)
Description: Stores the genre of the audio.
Example: "Rock", "Pop", or a numerical value representing a genre (e.g., "17" for Rock according to ID3v1).

4. TPUB (Publisher)
Description: Contains the name of the publishing company or label that released the audio.
Example: "EMI Records"

5. TKEY (Initial Key)
Description: The musical key in which the song starts.
Example: "C", "Am", "G#m"

6. TBPM (Beats Per Minute)
Description: Represents the tempo of the audio in beats per minute.
Example: "120" for 120 BPM.

7. TPE3 (Conductor/Performer Refinement)
Description: The name of the conductor or someone involved in the refinement of the performance.
Example: "John Doe (Conductor)"

8. TSRC (ISRC - International Standard Recording Code)
Description: Holds the International Standard Recording Code, a unique identifier for sound recordings.
Example: "USRC17607839"

9. APIC (Attached Picture)
Description: Used to embed images, such as album artwork, in the audio file.
Data Format: Includes a MIME type (e.g., "image/jpeg") and image data (e.g., cover art).
Example: A JPEG or PNG image of the album cover.

10. TDRC (Recording Time/Date)
Description: Stores the year and optionally the time of recording of the audio file.
Example: "2020" or "2020-12-01T12:30:00" for more precise timestamps."""

details_textbox.insert(END, details_text)
details_textbox.config(state=DISABLED)  # Make the text read-only

# Main loop
root.mainloop()


# Created by Alejandro X. Solis Owner of TechFusion Repairs LLC
# MIT License
# All Rights Reserved.
# See LICENSE file for more details.
# © 2024 TechFusion Repairs LLC. All rights reserved.