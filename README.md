# HarmonyHaven

**HarmonyHaven** is a comprehensive music management and playback tool developed by TechFusion Repairs LLC. It helps users organize their music collection, play songs, and manage duplicates, all within an easy-to-use interface.

## Features

- **Scan and Organize Music Files**: Easily scan directories and organize your music collection by ID3 tags (e.g., genre, artist, album).
- **Duplicate Finder**: Automatically detect and delete duplicate music files based on MD5 hash.
- **Music Playback**: Play music directly in the app, with options for pausing, stopping, and adjusting volume.
- **Search Music**: Quickly search for songs by name and view their locations.
- **Customizable Interface**: Change the app’s background color or set a background image to suit your preferences.
- **Logging**: All actions and results are displayed in a log window for easy monitoring.

## Installation

To install and run **HarmonyHaven**, follow these steps:

### Requirements
- Python 3.6 or higher
- The following Python libraries:
  - `pygame` (for audio playback)
  - `mutagen` (for handling metadata)
  - `pydub` (for audio processing)
  - `Pillow` (for image handling)

### Install Using `pip`

You can install HarmonyHaven and its dependencies using `pip`:

```bash
pip install HarmonyHaven

Or if you're installing it from the GitHub repository:
git clone https://github.com/TechFusionRepairs/HarmonyHaven.git
cd HarmonyHaven
pip install -r requirements.txt

How to Use
Here’s a brief guide on how to use the app:

Scanning Music Files
Navigate to the "File Operations" tab, click on Scan Directory, and choose a folder to scan. The number of music files found will be logged.

Finding Duplicate Files
After scanning, click the Find Duplicates button. If duplicates are found, you can delete them directly from the log window.

Playing Music
Go to the Music Playback tab, select a song, and click Play Selected Song. Use the pause, stop, and volume controls to manage playback.

Searching for Songs
In the Search Music tab, type a song name and click Search Song. The results will be displayed in the log window.

Organizing Music by ID3 Tags
In the Organize Music tab, select primary and subfolder tags to organize your music by metadata (e.g., Genre, Artist, Year).

Adding Subfolders for Organizing
Click Add Subfolder for Organizing to include additional music files from another directory.

Contributing
We welcome contributions to HarmonyHaven! If you'd like to help, feel free to:

Open issues for bugs or suggestions.
Fork the repository, make changes, and submit a pull request.
For major changes, please open an issue first to discuss what you would like to change.

License
HarmonyHaven is licensed under the MIT License. See the LICENSE file for more details.

Contact
For support, questions, or feedback, reach out to:

Developer: Alejandro X. Solis
Email: TechFusionRepairs@gmail.com
Website: TechFusion Repairs LLC

### Breakdown:
1. **Introduction**: Briefly introduces what HarmonyHaven does.
2. **Features**: Highlights the main capabilities of the app.
3. **Installation**: Provides installation steps using `pip` and via GitHub.
4. **How to Use**: Outlines the main usage instructions in a concise way.
5. **Contributing**: Encourages users to contribute to the project.
6. **License**: States the license under which the app is available.
7. **Contact**: Includes your name, email, and a link to your business.

This will give users a solid understanding of the app and how to get started, along with relevant links and documentation.
© 2024 TechFusion Repairs LLC. All rights reserved.